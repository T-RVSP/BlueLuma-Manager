import cloudscraper
import os
import re
import requests
import subprocess
import shutil
import json
import time
import sys
import logging

if sys.platform == "win32":
    import winreg
from contextlib import contextmanager
from bs4 import BeautifulSoup as parser
from requests.exceptions import ConnectionError, ConnectTimeout
from cloudscraper.exceptions import CloudflareException, CaptchaException

BASE_PATH = "{}/GLR_Manager".format(os.getenv("LOCALAPPDATA"))
PROFILES_PATH = "{}/Profiles".format(BASE_PATH)
CURRENT_VERSION = "1.0.1"
UPDATER_EXE = "BlueLuma Updater.exe"
GLINJECT_DIR_NAME = "GLinject"
GREENLUMA_DOWNLOAD_URL = "https://cs.rin.ru/forum/viewtopic.php?f=29&t=103709"
GREENLUMA_ZIP_PASSWORD = "cs.rin.ru"
GREENLUMA_NORMAL_MODE_DIR = "NormalMode"
GREENLUMA_STEALTH_MODE_DIR = "StealthMode"
STEAM_WAYBACK_CALENDAR_URL = "https://web.archive.org/web/20260000000000*/http://media.steampowered.com/client/"
STEAM_CFG_LINES = (
    "BootStrapperInhibitAll=Enable",
    "BootStrapperForceSelfUpdate=False",
)


def get_app_directory():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_glinject_path():
    path = os.path.join(get_app_directory(), GLINJECT_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

class Game:
    def __init__(self, id, name, type):
        self.id = id.strip()
        self.name = name.strip()
        self.type = type.strip()

    def to_JSON(self):
        return {"id": self.id, "name": self.name, "type": self.type}

    def to_string(self):
        return "ID: {0}\nName: {1}\nType: {2}\n".format(self.id, self.name, self.type)

    def to_list(self):
        return [self.id, self.name, self.type]

    def __eq__(self, value):
        return self.id == value.id and self.name == value.name and self.type == value.type

    def __getitem__(self, index):
        values_list = list(vars(self).values())
        return values_list[index]

    @staticmethod
    def from_JSON(data):
        return Game(data["id"], data["name"], data["type"])

    @staticmethod
    def from_table_list(list):
        games = []
        for i in range(int(len(list) / 3)):
            games.append(Game(list[i * 3], list[i * 3 + 1], list[i * 3 + 2]))

        return games

class Profile:
    def __init__(self, name="default", games=None, steam_id=""):
        self.name = name
        self.games = games if games is not None else []
        self.steam_id = str(steam_id or "")

    def add_game(self, game):
        self.games.append(game)

    def remove_game(self, game):
        if type(game) is Game:
            self.games.remove(game)
        else:
            for game_ in self.games:
                if game_.name == game:
                    self.games.remove(game_)
                    break

    def profile_filename(self):
        if self.steam_id:
            return "{0}.json".format(self.steam_id)
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", self.name).strip() or "profile"
        return "{0}.json".format(safe_name)

    def profile_filepath(self, path=PROFILES_PATH):
        return os.path.join(path, self.profile_filename())

    def export_profile(self, path=PROFILES_PATH):
        data = {
            "name": self.name,
            "steam_id": self.steam_id,
            "games": [game.to_JSON() for game in self.games],
        }
        with open(self.profile_filepath(path), "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

    def __eq__(self, value):
        return self.name == value.name

    @staticmethod
    def from_JSON(data):
        return Profile(
            data.get("name", "default"),
            [Game.from_JSON(game) for game in data.get("games", [])],
            data.get("steam_id", ""),
        )

class ProfileManager:
    def __init__(self):
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        if not os.path.exists(PROFILES_PATH):
            os.makedirs(PROFILES_PATH)

        for filename in os.listdir(PROFILES_PATH):
            if os.path.splitext(filename)[1] != ".json":
                continue
            filepath = os.path.join(PROFILES_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    self.register_profile(Profile.from_JSON(data))
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    logging.exception(e)

    def register_profile(self, profile):
        self.profiles[profile.name] = profile

    def create_profile(self, name, games=None, steam_id=""):
        if name == "":
            return

        self.register_profile(Profile(name, games, steam_id=steam_id))
        self.profiles[name].export_profile(PROFILES_PATH)

    def rename_profile(self, old_name, new_name):
        if not new_name or old_name == new_name or old_name not in self.profiles:
            return

        profile = self.profiles.pop(old_name)
        old_path = profile.profile_filepath(PROFILES_PATH)
        profile.name = new_name
        self.profiles[new_name] = profile
        profile.export_profile(PROFILES_PATH)

        if os.path.isfile(old_path) and os.path.normcase(old_path) != os.path.normcase(profile.profile_filepath(PROFILES_PATH)):
            try:
                os.remove(old_path)
            except OSError as err:
                logging.warning("Impossible de supprimer l'ancien profil %s : %s", old_path, err)

    def remove_profile(self, profile_name):
        if profile_name not in self.profiles:
            return

        profile = self.profiles.pop(profile_name)
        filepath = profile.profile_filepath(PROFILES_PATH)
        if os.path.isfile(filepath):
            os.remove(filepath)

class Config:
    def __init__(self, steam_path="", greenluma_path="", no_hook=False, version=CURRENT_VERSION, last_profile="default", check_update=True, use_steamdb=False, manager_msg=False):
        self.steam_path = steam_path
        self.greenluma_path = greenluma_path
        self.no_hook = no_hook
        self.version = version
        self.last_profile = last_profile
        self.check_update = check_update
        self.use_steamdb = use_steamdb
        self.manager_msg = manager_msg

    def export_config(self):
        with open("{}/config.json".format(BASE_PATH), "w") as outfile:
            json.dump(vars(self), outfile, indent=4)

    @staticmethod
    def from_JSON(data):
        config = Config()
        for key, value in data.items():
            if key in vars(config).keys():
                setattr(config, key, value)

        return config

    @staticmethod
    def load_config():
        if not os.path.isfile("{}/config.json".format(BASE_PATH)):
            if not os.path.exists(BASE_PATH):
                os.makedirs(BASE_PATH)

            config = Config()
            ensure_steam_path(config)
            ensure_greenluma_path(config)
            config.export_config()
            return config
        else:
            with open("{}/config.json".format(BASE_PATH), "r") as file_:
                try:
                    data = json.load(file_)
                    config = Config.from_JSON(data)
                except Exception as e:
                    logging.exception(e)
                    config = Config()

                config.no_hook = False
                config.version = CURRENT_VERSION
                ensure_steam_path(config)
                ensure_greenluma_path(config)
                config.export_config()
                return config

class ConfigNotLoadedException(Exception):
    pass


def is_valid_steam_path(path):
    return bool(path) and os.path.isdir(path) and os.path.isfile(os.path.join(path, "Steam.exe"))


def is_valid_greenluma_path(path):
    return bool(path) and os.path.isdir(path) and os.path.isfile(os.path.join(path, "DLLInjector.exe"))


def find_greenluma_runtime_path(glinject_root=None, stealth=False):
    """Retourne le dossier contenant DLLInjector.exe (NormalMode ou StealthMode)."""
    root = os.path.abspath(glinject_root or get_glinject_path())
    preferred = GREENLUMA_STEALTH_MODE_DIR if stealth else GREENLUMA_NORMAL_MODE_DIR
    search_order = [preferred]
    for folder in (GREENLUMA_NORMAL_MODE_DIR, GREENLUMA_STEALTH_MODE_DIR):
        if folder not in search_order:
            search_order.append(folder)

    for folder in search_order:
        candidate = os.path.join(root, folder)
        if is_valid_greenluma_path(candidate):
            return candidate

    if is_valid_greenluma_path(root):
        return root

    return os.path.join(root, preferred)


def greenluma_is_installed(stealth=False):
    return is_valid_greenluma_path(find_greenluma_runtime_path(stealth=stealth))


def extract_greenluma_archive(zip_path):
    """Extrait l'archive BlueLuma dans GLinject/ avec le mot de passe cs.rin.ru."""
    import pyzipper

    zip_path = os.path.abspath(zip_path)
    if not os.path.isfile(zip_path):
        raise FileNotFoundError("Fichier ZIP introuvable.")

    dest = get_glinject_path()
    password = GREENLUMA_ZIP_PASSWORD.encode("utf-8")
    last_error = None

    for zip_cls in (pyzipper.AESZipFile, pyzipper.ZipFile):
        try:
            with zip_cls(zip_path) as archive:
                archive.pwd = password
                archive.extractall(dest)
            last_error = None
            break
        except Exception as err:
            last_error = err

    if last_error is not None:
        raise RuntimeError("Impossible d'extraire l'archive. Vérifiez le mot de passe et le fichier ZIP.") from last_error

    if not greenluma_is_installed(stealth=False) and not greenluma_is_installed(stealth=True):
        raise RuntimeError(
            "Archive extraite, mais DLLInjector.exe est introuvable dans GLinject. "
            "Vérifiez que vous avez sélectionné la bonne archive BlueLuma 2026."
        )

    logging.info("BlueLuma extrait dans %s", dest)
    return dest


def _registry_steam_paths():
    if sys.platform != "win32":
        return []

    paths = []
    keys = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
    )
    value_names = ("InstallPath", "SteamPath")

    for hkey, subkey in keys:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                for name in value_names:
                    try:
                        value, _ = winreg.QueryValueEx(key, name)
                        if value:
                            paths.append(value.replace("/", os.sep))
                    except OSError:
                        pass
        except OSError:
            pass

    return paths


def _default_steam_paths():
    candidates = []
    for env_name in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(env_name)
        if base:
            candidates.append(os.path.join(base, "Steam"))

    # Emplacements fréquents si les variables d'environnement sont absentes
    candidates.extend([
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
    ])
    return candidates


def _steam_from_running_process():
    try:
        import psutil
    except ImportError:
        return ""

    for process in psutil.process_iter(["exe"]):
        try:
            exe = process.info.get("exe")
            if exe and os.path.basename(exe).lower() == "steam.exe":
                return os.path.dirname(exe)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return ""


def detect_steam_path():
    """Tente de localiser automatiquement l'installation Steam."""
    seen = set()
    candidates = []

    def add(path):
        if not path:
            return
        norm = os.path.normcase(os.path.abspath(path))
        if norm not in seen:
            seen.add(norm)
            candidates.append(os.path.abspath(path))

    for path in _registry_steam_paths():
        add(path)

    add(_steam_from_running_process())

    for path in _default_steam_paths():
        add(path)

    for path in candidates:
        if is_valid_steam_path(path):
            logging.info("Steam détecté automatiquement : %s", path)
            return path

    return ""


def _registry_steam_exe():
    if sys.platform != "win32":
        return ""

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            value, _ = winreg.QueryValueEx(key, "SteamExe")
            if value:
                path = os.path.abspath(value.replace("/", os.sep))
                if os.path.isfile(path):
                    return path
    except OSError:
        pass

    return ""


def get_steam_exe_path():
    global config
    if config and is_valid_steam_path(config.steam_path):
        return os.path.join(os.path.abspath(config.steam_path), "Steam.exe")

    registry_exe = _registry_steam_exe()
    if registry_exe:
        return registry_exe

    raise RuntimeError("Steam introuvable. Configurez le chemin Steam dans les paramètres.")


def get_steam_directory():
    return os.path.dirname(get_steam_exe_path())


def normalize_steam_downgrade_url(raw_url):
    """Transforme une URL Wayback en URL overridepackageurl valide pour Steam."""
    url = raw_url.strip()
    if not url:
        raise ValueError("Veuillez coller une URL Wayback Machine.")

    match = re.search(r"web\.archive\.org/web/(\d+)(?:if_)?/", url, re.IGNORECASE)
    if not match:
        raise ValueError(
            "URL Wayback invalide. Copiez le lien depuis le calendrier media.steampowered.com "
            "(clic droit sur l'heure → Copier l'adresse du lien)."
        )

    timestamp = match.group(1)
    return "http://web.archive.org/web/{0}if_/media.steampowered.com/client".format(timestamp)


def is_steam_running():
    try:
        import psutil
    except ImportError:
        return False

    targets = {"steam.exe", "steamservice.exe", "steamwebhelper.exe"}
    for process in psutil.process_iter(["name"]):
        try:
            name = (process.info.get("name") or "").lower()
            if name in targets:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False


def close_steam_for_downgrade(timeout=30):
    if not is_steam_running():
        return True

    try:
        steam_exe = get_steam_exe_path()
        steam_dir = get_steam_directory()
        subprocess.run([steam_exe, "-shutdown"], cwd=steam_dir, timeout=15)
    except Exception as err:
        logging.warning("Steam -shutdown a échoué : %s", err)

    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_steam_running():
            return True
        time.sleep(0.5)

    if sys.platform == "win32":
        for process_name in ("steam.exe", "SteamService.exe", "steamwebhelper.exe"):
            subprocess.run(
                ["taskkill", "/f", "/im", process_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        time.sleep(2)

    return not is_steam_running()


def write_steam_cfg(steam_dir=None):
    target_dir = steam_dir or get_steam_directory()
    cfg_path = os.path.join(target_dir, "steam.cfg")
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(STEAM_CFG_LINES) + "\n")
    logging.info("steam.cfg créé : %s", cfg_path)
    return cfg_path


def get_steam_cfg_path(steam_dir=None):
    target_dir = steam_dir or get_steam_directory()
    return os.path.join(target_dir, "steam.cfg")


def has_steam_cfg(steam_dir=None):
    return os.path.isfile(get_steam_cfg_path(steam_dir))


def remove_steam_cfg(steam_dir=None):
    cfg_path = get_steam_cfg_path(steam_dir)
    if os.path.isfile(cfg_path):
        os.remove(cfg_path)
        logging.info("steam.cfg supprimé : %s", cfg_path)
        return True
    return False


def perform_steam_downgrade(raw_url):
    package_url = normalize_steam_downgrade_url(raw_url)
    steam_exe = get_steam_exe_path()
    steam_dir = get_steam_directory()

    if not close_steam_for_downgrade():
        raise RuntimeError(
            "Impossible de fermer Steam. Fermez-le complètement (y compris la zone de notification) puis réessayez."
        )

    write_steam_cfg(steam_dir)
    subprocess.Popen(
        [
            steam_exe,
            "-forcesteamupdate",
            "-forcepackagedownload",
            "-overridepackageurl",
            package_url,
            "-exitsteam",
        ],
        cwd=steam_dir,
    )
    logging.info("Downgrade Steam lancé avec %s", package_url)
    return package_url


def perform_steam_restore():
    """Supprime steam.cfg et force la réinstallation de la dernière version officielle."""
    steam_exe = get_steam_exe_path()
    steam_dir = get_steam_directory()

    if not close_steam_for_downgrade():
        raise RuntimeError(
            "Impossible de fermer Steam. Fermez-le complètement (y compris la zone de notification) puis réessayez."
        )

    remove_steam_cfg(steam_dir)
    subprocess.Popen(
        [
            steam_exe,
            "-forcesteamupdate",
            "-forcepackagedownload",
            "-exitsteam",
        ],
        cwd=steam_dir,
    )
    logging.info("Restauration Steam lancée (mise à jour officielle)")
    return True


def _parse_vdf_quoted_value(block, key):
    match = re.search(r'"{0}"\s+"((?:\\.|[^"\\])*)"'.format(re.escape(key)), block)
    if not match:
        return ""
    return match.group(1).replace('\\"', '"').replace("\\\\", "\\")


def get_steam_saved_accounts(steam_path):
    """Retourne les comptes Steam mémorisés (pseudo + identifiant) depuis loginusers.vdf."""
    if not is_valid_steam_path(steam_path):
        return []

    vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
    if not os.path.isfile(vdf_path):
        logging.info("loginusers.vdf introuvable : %s", vdf_path)
        return []

    try:
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as file_:
            content = file_.read()
    except OSError as err:
        logging.warning("Impossible de lire loginusers.vdf : %s", err)
        return []

    accounts = []
    seen_ids = set()
    for block_match in re.finditer(r'"(\d{17})"\s*\{', content):
        steam_id = block_match.group(1)
        if steam_id in seen_ids:
            continue

        start = block_match.end()
        depth = 1
        index = start
        while index < len(content) and depth > 0:
            char = content[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1

        block = content[start:index - 1]
        account_name = _parse_vdf_quoted_value(block, "AccountName")
        persona_name = _parse_vdf_quoted_value(block, "PersonaName")
        display_name = persona_name or account_name or steam_id

        accounts.append({
            "steam_id": steam_id,
            "account_name": account_name,
            "persona_name": display_name,
        })
        seen_ids.add(steam_id)

    accounts.sort(key=lambda item: item["persona_name"].lower())
    logging.info("%d compte(s) Steam détecté(s)", len(accounts))
    return accounts


def sync_profiles_from_steam(profile_manager, steam_path, last_profile=""):
    """Synchronise les profils locaux avec les comptes enregistrés sur Steam."""
    accounts = get_steam_saved_accounts(steam_path)
    if not accounts:
        return False, {}

    renamed = {}
    by_steam_id = {}
    for profile in profile_manager.profiles.values():
        if profile.steam_id:
            by_steam_id[profile.steam_id] = profile

    active_ids = set()
    for account in accounts:
        steam_id = account["steam_id"]
        persona_name = account["persona_name"]
        active_ids.add(steam_id)

        if steam_id in by_steam_id:
            profile = by_steam_id[steam_id]
            if profile.name != persona_name:
                old_name = profile.name
                profile_manager.rename_profile(old_name, persona_name)
                renamed[old_name] = persona_name
                profile = profile_manager.profiles[persona_name]
            profile.steam_id = steam_id
            profile.export_profile(PROFILES_PATH)
            continue

        if persona_name in profile_manager.profiles:
            profile = profile_manager.profiles[persona_name]
            legacy_path = profile.profile_filepath(PROFILES_PATH)
            profile.steam_id = steam_id
            profile.export_profile(PROFILES_PATH)
            if os.path.isfile(legacy_path) and os.path.normcase(legacy_path) != os.path.normcase(profile.profile_filepath(PROFILES_PATH)):
                try:
                    os.remove(legacy_path)
                except OSError as err:
                    logging.warning("Impossible de supprimer l'ancien profil %s : %s", legacy_path, err)
            by_steam_id[steam_id] = profile
            continue

        profile_manager.create_profile(persona_name, steam_id=steam_id)
        by_steam_id[steam_id] = profile_manager.profiles[persona_name]

    for profile_name, profile in list(profile_manager.profiles.items()):
        if profile.steam_id and profile.steam_id not in active_ids:
            profile_manager.remove_profile(profile_name)
        elif profile_name == "default" and not profile.steam_id:
            profile_manager.remove_profile(profile_name)

    return True, renamed


def ensure_steam_path(config):
    if is_valid_steam_path(config.steam_path):
        config.steam_path = os.path.abspath(config.steam_path)
        return True

    detected = detect_steam_path()
    if detected:
        config.steam_path = detected
        return True

    return False


def ensure_greenluma_path(config):
    config.no_hook = False
    glinject = get_glinject_path()
    runtime = find_greenluma_runtime_path(glinject, stealth=False)
    config.greenluma_path = runtime

    if is_valid_greenluma_path(runtime):
        logging.info("BlueLuma trouvé dans GLinject : %s", runtime)
    else:
        logging.info(
            "Dossier GLinject prêt : %s — BlueLuma non installé (DLLInjector.exe manquant)",
            glinject,
        )

    return True


STEAM_APP_CACHE_PATH = os.path.join(BASE_PATH, "steam_app_cache.json")
STEAM_SKIP_APPIDS = {
    "228980",   # Steamworks Common Redistributables
    "1070560",  # Steam Linux Runtime
    "1391110",  # Steam Linux Runtime
    "1493710",  # Proton
    "1628350",  # Steamworks Common Redistributables
}
STEAM_SKIP_NAME_PARTS = (
    "steamworks",
    "proton",
    "steam linux runtime",
    "directx",
    "redistributable",
    "vcredist",
)


def _parse_acf_value(content, key):
    match = re.search(rf'"{re.escape(key)}"\s+"((?:\\.|[^"\\])*)"', content)
    if not match:
        return ""
    return match.group(1).replace("\\\\", "\\").replace('\\"', '"')


def get_steam_library_folders(steam_path):
    folders = []
    seen = set()

    def add(path):
        if not path:
            return
        abs_path = os.path.abspath(path)
        key = os.path.normcase(abs_path)
        if key not in seen and os.path.isdir(abs_path):
            seen.add(key)
            folders.append(abs_path)

    add(steam_path)

    for rel_path in ("steamapps/libraryfolders.vdf", "config/libraryfolders.vdf"):
        vdf_path = os.path.join(steam_path, rel_path)
        if not os.path.isfile(vdf_path):
            continue
        try:
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as file_:
                content = file_.read()
            for match in re.finditer(r'"path"\s+"((?:\\.|[^"\\])*)"', content):
                add(match.group(1).replace("\\\\", "\\"))
        except OSError as err:
            logging.warning("Impossible de lire %s : %s", vdf_path, err)
        break

    return folders


def scan_installed_steam_apps(steam_path):
    installed = {}

    for library in get_steam_library_folders(steam_path):
        steamapps = os.path.join(library, "steamapps")
        if not os.path.isdir(steamapps):
            continue

        for filename in os.listdir(steamapps):
            if not filename.startswith("appmanifest_") or not filename.endswith(".acf"):
                continue

            manifest_path = os.path.join(steamapps, filename)
            try:
                with open(manifest_path, "r", encoding="utf-8", errors="ignore") as file_:
                    content = file_.read()
            except OSError:
                continue

            appid = _parse_acf_value(content, "appid")
            name = _parse_acf_value(content, "name")
            if appid and name:
                installed[appid] = name

    return installed


def _should_skip_steam_app(appid, name):
    if appid in STEAM_SKIP_APPIDS:
        return True
    name_lower = name.lower()
    return any(part in name_lower for part in STEAM_SKIP_NAME_PARTS)


def _load_steam_app_cache():
    if not os.path.isfile(STEAM_APP_CACHE_PATH):
        return {}
    try:
        with open(STEAM_APP_CACHE_PATH, "r", encoding="utf-8") as file_:
            return json.load(file_)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_steam_app_cache(cache):
    try:
        os.makedirs(BASE_PATH, exist_ok=True)
        with open(STEAM_APP_CACHE_PATH, "w", encoding="utf-8") as file_:
            json.dump(cache, file_)
    except OSError as err:
        logging.warning("Impossible d'enregistrer le cache Steam : %s", err)


def get_steam_app_metadata(appid, cache=None, include_dlc_list=True):
    if cache is None:
        cache = _load_steam_app_cache()

    cached = cache.get(str(appid))
    if cached:
        has_name = bool(cached.get("name"))
        has_dlc = "dlc" in cached
        if has_name and (not include_dlc_list or has_dlc):
            return cached

    filters = "basic,dlc" if include_dlc_list else "basic"
    metadata = {"type": "game", "name": "", "dlc": cached.get("dlc", []) if cached else []}
    try:
        response = requests.get(
            "https://store.steampowered.com/api/appdetails",
            params={"appids": appid, "filters": filters},
            timeout=12,
        )
        payload = response.json().get(str(appid), {})
        if payload.get("success"):
            data = payload.get("data", {})
            metadata = {
                "type": data.get("type", "game"),
                "name": data.get("name", ""),
                "dlc": data.get("dlc", metadata.get("dlc", [])),
            }
    except (ConnectionError, ConnectTimeout, ValueError, requests.RequestException) as err:
        logging.debug("Métadonnées Steam indisponibles pour %s : %s", appid, err)

    cache[str(appid)] = metadata
    return metadata


def resolve_steam_app_name(appid, cache, installed):
    appid = str(appid)
    if appid in installed:
        return installed[appid]

    cached = cache.get(appid)
    if cached and cached.get("name"):
        return cached["name"]

    metadata = get_steam_app_metadata(appid, cache, include_dlc_list=False)
    if metadata.get("name"):
        return metadata["name"]

    return "DLC {0}".format(appid)


def _steam_store_slug(name):
    slug = re.sub(r"[^\w\s-]", "", name)
    return slug.replace(" ", "_")


def fetch_game_dlcs(appid, game_name):
    """Récupère tous les DLC d'un jeu avec leurs noms (1 requête par page de 64)."""
    slug = _steam_store_slug(game_name) if game_name else "game"
    all_dlcs = []
    start = 0
    page_size = 64

    while True:
        try:
            response = requests.get(
                "https://store.steampowered.com/dlc/{0}/{1}/ajaxgetfilteredrecommendations".format(appid, slug),
                params={"sort": "newreleases", "count": page_size, "start": start},
                timeout=15,
            )
        except (ConnectionError, ConnectTimeout, requests.RequestException) as err:
            logging.debug("Liste DLC indisponible pour %s : %s", appid, err)
            break

        if not response.text.startswith("{"):
            break

        payload = response.json()
        if not payload.get("success"):
            break

        dlcs = parseDlcs(payload.get("results_html", ""))
        all_dlcs.extend(dlcs)
        start += page_size
        total = payload.get("total_count", 0)
        if start >= total or not dlcs:
            break

    return all_dlcs


def _cache_dlc_names(dlcs, cache):
    for dlc in dlcs:
        cache[str(dlc.id)] = {"type": "dlc", "name": dlc.name, "dlc": []}


def get_installed_games_with_extensions(steam_path):
    """Retourne les jeux installés et tous leurs DLC/extensions (via l'API Steam)."""
    if not is_valid_steam_path(steam_path):
        return []

    installed = scan_installed_steam_apps(steam_path)
    if not installed:
        return []

    cache = _load_steam_app_cache()
    result = []
    seen_ids = set()
    game_ids = []

    for appid, manifest_name in installed.items():
        if _should_skip_steam_app(appid, manifest_name):
            continue

        metadata = get_steam_app_metadata(appid, cache)
        app_type = metadata.get("type", "game")
        if app_type == "dlc":
            continue
        if app_type in ("game", "demo", "beta"):
            game_ids.append(appid)

    for appid in sorted(game_ids, key=lambda app_id: installed[app_id].lower()):
        name = installed[appid]
        result.append(Game(appid, name, "Game"))
        seen_ids.add(appid)

        metadata = get_steam_app_metadata(appid, cache)
        dlcs = fetch_game_dlcs(appid, name)

        if not dlcs:
            for dlc_id in metadata.get("dlc", []):
                dlc_id = str(dlc_id)
                if dlc_id in seen_ids:
                    continue
                dlc_name = resolve_steam_app_name(dlc_id, cache, installed)
                dlcs.append(Game(dlc_id, dlc_name, "DLC"))

        _cache_dlc_names(dlcs, cache)
        for dlc in dlcs:
            if dlc.id not in seen_ids:
                result.append(dlc)
                seen_ids.add(dlc.id)

    for appid, manifest_name in installed.items():
        if appid in seen_ids or _should_skip_steam_app(appid, manifest_name):
            continue

        metadata = get_steam_app_metadata(appid, cache)
        if metadata.get("type") == "dlc":
            result.append(Game(appid, manifest_name, "DLC"))
            seen_ids.add(appid)

    _save_steam_app_cache(cache)

    if len(result) > 168:
        logging.warning(
            "BlueLuma limite l'AppList à 168 jeux. %d entrées détectées — retirez-en avant de générer.",
            len(result),
        )

    logging.info("%d entrée(s) importée(s) depuis la bibliothèque Steam", len(result))
    return result


#-------------
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s", handlers=[logging.FileHandler("errors.log", mode="w"), logging.StreamHandler()])
logging.info("BlueLuma Manager " + CURRENT_VERSION)
config = Config.load_config()
query_filter = re.compile("[ \u00a9\u00ae\u2122]")

@contextmanager
def get_config():
    global config
    try:
        if config:
            yield config
        else:
            config = Config.load_config()
    finally:
        config.export_config()

def createFiles(games):
    if not os.path.exists("{}/AppList".format(config.greenluma_path)):
        os.makedirs("{}/AppList".format(config.greenluma_path))
    else:
        shutil.rmtree("{}/AppList".format(config.greenluma_path))
        time.sleep(0.5)
        os.makedirs("{}/AppList".format(config.greenluma_path))

    for i in range(len(games)):
        with open("{}/AppList/{}.txt".format(config.greenluma_path, i), "w") as file:
            file.write(games[i].id)

def parseSteamDB(html):
    p = parser(html, "html.parser")

    rows = p.find_all("tr", class_="app")

    games = []
    for row in rows:
        data = row("td")
        if data[1].get_text() != "Unknown":
            game = Game(data[0].get_text(), data[2].get_text(), data[1].get_text())
            games.append(game)

    return games

def parseDlcs(html):
    p = parser(html, "html.parser")

    dlcs = p.find_all("div", class_="recommendation")

    games = []
    for dlc in dlcs:
        appid = dlc.find("a")["data-ds-appid"]
        name = dlc.find("span", class_="color_created").get_text()
        games.append(Game(appid, name, "DLC"))

    return games

def getDlcs(storeUrl):
    if "app/" not in storeUrl:
        return []
    appinfo = storeUrl.split("app/")[1].split("/")
    appid = appinfo[0]
    game_name = appinfo[1].replace("_", " ").replace("-", " ") if len(appinfo) > 1 and appinfo[1] else ""
    return fetch_game_dlcs(appid, game_name)

def parseGames(html, query):
    query = query_filter.sub("", query.lower())
    p = parser(html, "html.parser")

    results = p.find_all("a", class_="search_result_row")

    games = []
    for result in results:
        if result.has_attr("data-ds-appid"):
            appid = result["data-ds-appid"]
            name = result.find("span", class_="title").get_text()
            # Filter out garbage
            if "," not in appid and query in query_filter.sub("", name.lower()):
                games.append(Game(appid, name, "Game"))
                games.extend(getDlcs(result["href"]))

    return games

def queryfy(input_):
    arr = input_.split()
    result = arr.pop(0)
    for word in arr:
        result = result + "+" + word
    print(result)
    return result

def queryGames(query):
    try:
        if config.use_steamdb and False:
            scraper = cloudscraper.create_scraper()
            params = {"a": "app", "q": query, "type": -1, "category": 0}
            response = scraper.get("https://steamdb.info/search/", params=params)
            return parseSteamDB(response.content)
        else:
            params = {"term": query, "count": 25, "start": 0, "category1": 998}
            response = requests.get("https://store.steampowered.com/search/results", params=params)
            return parseGames(response.text, query)
    except (ConnectionError, ConnectTimeout, CloudflareException, CaptchaException) as err:
        logging.exception(err)
        return err

def runUpdater():
    if "-NoUpdate" not in sys.argv and config.check_update and os.path.exists(UPDATER_EXE):
        try:
            subprocess.run(UPDATER_EXE)
        except OSError as err:
            logging.error("Error while checking for updates")
            logging.exception(err)

    # Post update measure
    if "-PostUpdate" in sys.argv:
        for fl in os.listdir("./"):
            if fl.startswith("new_"):
                real_name = fl.replace("new_", "")
                os.remove(real_name)
                os.rename(fl, real_name)
