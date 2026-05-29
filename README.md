# BlueLuma-Manager

Une application pour gérer le dossier AppList du déverrouilleur Steam « BlueLuma »

Il s’agit d’un Remake de GreenLuma Manager afin de mieux prendre en charge :

- Une interface sombre moderne entièrement en **français**
- Les **comptes Steam enregistrés** comme profils (pseudo automatique)
- L’**import automatique** des jeux et DLC installés
- La **génération automatique de l’AppList** (sans bouton manuel)
- Un **éditeur manuel** pour les jeux / DLC non détectés
- L’installation de BlueLuma dans **`GLinject/`** via ZIP cs.rin.ru
- Le **downgrade et la restauration** de Steam depuis les paramètres
- Les **mises à jour** via le dépôt GitHub T-RVSP

**Développé par [ShyninG](https://github.com/T-RVSP)** — Version **1.0.1**

---

## Dernière version : **[BlueLuma Manager](https://github.com/T-RVSP/BlueLuma-Manager/releases)**

---

## Installation

```bash
pip install -r requirements.txt
python main.py
```

---

## Qu’est-ce que BlueLuma ?

BlueLuma est un déverrouilleur Steam créé par **ShyninG** permettant d’obtenir des jeux via les bibliothèques partagées en famille ainsi que des DLC pour les jeux.  
Il offre cependant bien plus de fonctionnalités.

**BlueLuma Manager** est l’interface graphique qui prépare le dossier `AppList`, gère vos jeux par compte Steam et lance l’injecteur depuis le dossier local `GLinject/`.

Téléchargement du moteur GreenLuma (requis séparément) : [cs.rin.ru — topic 103709](https://cs.rin.ru/forum/viewtopic.php?f=29&t=103709)

### Liste complète des fonctionnalités fournies par ShyninG

- Gestionnaire graphique **BlueLuma Manager** (PyQt5)
- Synchronisation des profils avec les comptes Steam mémorisés (`loginusers.vdf`)
- Affichage du **pseudo Steam** dans le sélecteur « Compte Steam »
- Import automatique de la bibliothèque Steam installée + DLC au démarrage
- Liste **Jeux/DLC Actif** par compte
- **AppList synchronisée automatiquement** à chaque ajout, suppression ou changement de compte
- Éditeur manuel (ID, nom, type Game/DLC) avec bouton **Activer**
- Boutons **Lancer** (BlueLuma) et **Retirer** (jeu du profil)
- Dossier **`GLinject/`** auto-créé à la racine de l’app
- Installation assistée si `DLLInjector.exe` est absent (ZIP + mot de passe `cs.rin.ru`)
- Détection automatique du chemin Steam
- Paramètres : chemins, downgrade Steam (Wayback Machine), restauration (`steam.cfg`)
- Mises à jour optionnelles au démarrage via **BlueLuma Updater.exe**
- Profils sauvegardés en JSON (`%LOCALAPPDATA%/GLR_Manager/Profiles/`)

---

## Fonctionnalités

### Interface
- Thème sombre moderne, layouts responsifs
- Interface 100 % en français
- Paramètres accessibles via l’icône engrenage (à droite de l’éditeur)

### Comptes Steam
- Un profil = un compte Steam enregistré sur la machine
- Renommage automatique si le pseudo Steam change
- Conservation des jeux/DLC par compte (fichier `{steam_id}.json`)

### Jeux / DLC actifs
- Panneau droit : liste des jeux et DLC du compte sélectionné
- Suppression avec **Retirer** (bouton rouge)
- Lancement de BlueLuma avec **Lancer** (ferme Steam si nécessaire, puis `DLLInjector.exe`)
- Limite technique : **168 entrées** maximum par AppList

### Éditeur central
- Tableau vide au démarrage — ajout de lignes via **+**
- Colonnes : ID Steam, nom, type (Game / DLC)
- **Activer** : ajoute les entrées valides au profil actif

### GLinject / BlueLuma
- Chemin actif : `GLinject/NormalMode/`
- AppList générée dans `GLinject/NormalMode/AppList/`
- Mode furtif retiré — utilisation du mode normal uniquement

### Données locales

| Élément | Emplacement |
|--------|-------------|
| Configuration | `%LOCALAPPDATA%/GLR_Manager/config.json` |
| Profils | `%LOCALAPPDATA%/GLR_Manager/Profiles/` |
| AppList | `GLinject/NormalMode/AppList/` |
| Logs | `errors.log` |

---

## Puis-je être banni pour avoir utilisé BlueLuma ?

Il y aura toujours un risque en l'utilisant.  
Si vous êtes prêt à prendre ce risque, libre à vous de continuer.  
Sinon, mieux vaut éviter — surtout lorsque cela peut affecter le statut de votre compte Steam.

Comme prévu, certains jeux blacklistent BlueLuma et son utilisation peut entraîner un bannissement du jeu.  
Certains jeux vérifient la présence des fichiers de BlueLuma ou du gestionnaire dans le dossier Steam.  
D’autres effectuent des vérifications côté serveur concernant la possession des jeux et DLC.

Gardez également à l’esprit que, comme CreamAPI, BlueLuma **ne fonctionne pas** avec tous les jeux.  
De plus, tous les jeux ne sont pas forcément jouables via le partage familial Steam.

---

## Projets futurs

- Icône et assets visuels BlueLuma (remplacer les ressources GreenLuma restantes)
- Recherche Steam intégrée depuis l’éditeur (sans quitter l’app)
- Avertissement si BlueLuma ou le manager sont placés dans le dossier Steam
- Chargement des jeux déjà présents dans un dossier AppList existant
- Import de tous les DLC d’un jeu (au-delà de certaines limites API)
- Packaging `.exe` avec PyInstaller + release automatique GitHub Actions
- Documentation utilisateur et captures d’écran à jour

---

## Construit avec

* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) — Framework d’interface graphique
* [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/index.html) — Utilisé pour créer l’exécutable autonome
* Python 3 — Logique métier, Steam, profils, AppList
* C# (`GLMUpdater/`) — Mises à jour automatiques

---

## Crédits

| Auteur | Rôle |
|--------|------|
| **[ShyninG](https://github.com/T-RVSP)** | BlueLuma Manager — développement principal |
| **[BlueAmulet](https://github.com/BlueAmulet)** | Fork GreenLuma 2024 Manager |
| **[ImaniiTy](https://github.com/ImaniiTy)** | GreenLuma Reborn Manager (original) |
| **Steam006** | GreenLuma (moteur sous-jacent) |

## Licence

Voir le fichier [LICENSE](LICENSE).
```
