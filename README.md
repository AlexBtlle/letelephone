# Livre d’Or Audio - Le Téléphone

Un **système interactif de livre d’or audio** basé sur Raspberry Pi permettant de recueillir des messages vocaux lors d’un événement (par exemple, un mariage). Les invités décrochent un combiné de téléphone ancien, entendent une annonce d’accueil, puis enregistrent leur message qui est stocké sur une clé USB.

---

## Fonctionnalités

- **Détection du combiné** : Hook switch (GPIO) détecte le décrochage et le raccrochage.
- **Annonce sonore** : Lecture automatique d’un fichier MP3 d’accueil dès le décrochage.
- **Enregistrement audio** : Démarrage automatique de l’enregistrement après l’annonce, fin lors du raccrochage.
- **Durée maximale** : Timer configurable pour limiter la durée d’enregistrement.
- **Stockage sur clé USB** : Montage automatique, vérification d’intégrité et gestion de l’espace libre.
- **Configuration dynamique** : Paramètres (GPIO, durées, chemins) modifiables via un fichier JSON/YAML sur la clé USB.
- **Journalisation** : Logs d’événements (décrochage, début/arrêt, erreurs) enregistrés sur la clé.
- **Interface visuelle** : Écran OLED I2C 128×64 affiche l’état, la durée, l’espace et les erreurs en temps réel.
- **Démarrage autonome** : Lancement du service Python au boot via systemd.

> **Évolution future** : Interface Web pour consulter et écouter les messages à distance.

---

## Architecture du projet

```
projet-livre-dor-audio/
├── README.md
├── .gitignore
├── requirements.txt
├── src/
│   ├── main.py          # Script principal
│   ├── detection.py     # Gestion GPIO
│   ├── audio.py         # Lecture et enregistrement
│   ├── display.py       # Pilotage de l’écran OLED
│   └── utils.py         # Fonctions utilitaires
├── config/
│   └── config.json      # Paramètres modifiables
├── audio/
│   ├── annonces/        # MP3 d’accueil et messages d’erreur
│   └── enregistrements/ # Fichiers WAV/MP3 enregistrés
└── logs/                # Fichiers de journalisation
```

---

## Installation & Mise en route

1. **Cloner le dépôt** (via l’interface web ou `git clone`):
   ```bash
   git clone https://github.com/<votre‑utilisateur>/livre-dor-audio.git
   cd livre-dor-audio
   ```
2. **Créer un environnement virtuel Python** :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Installer les dépendances** :
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configurer le Raspberry Pi** :
   - Activer I2C (`raspi-config`).
   - Forcer la sortie audio jack : `amixer cset numid=3 1`.
5. **Préparer la clé USB** :
   - Créer un fichier `config/config.json` avec les paramètres.
   - Copier les annonces MP3 dans `audio/annonces/`.
6. **Installer le service systemd** :
   ```bash
   sudo cp deploy/livre_dor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable livre_dor.service
   sudo systemctl start livre_dor.service
   ```

---

## Utilisation

- **Monitoring** : L’écran OLED affiche l’état en temps réel.
- **Emplacement des fichiers** :
  - Enregistrements ➔ `audio/enregistrements/`
  - Logs ➔ `logs/`
- **Paramètres** : modifier `config/config.json` sur la clé USB et redémarrer le service.

---

## Contribuer

- **Branches** : `main` (stable), `dev` (intégration), `feature/<nom>`.
- **Commits sémantiques** (feat, fix, chore, docs, refactor).
- **Tests** : ajouter des tests unitaires et valider via CI (GitHub Actions).

---

## Licence

Ce projet est sous licence GNU GPLv3. Consultez le fichier `LICENSE` pour plus de détails.

