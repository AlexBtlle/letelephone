# Livre d’Or Audio

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
│   ├── detection.py     # Gestion GPIO (hook switch)
│   ├── audio.py         # Lecture et enregistrement audio
│   ├── display.py       # Pilotage de l’écran OLED (optionnel)
│   └── utils.py         # Fonctions utilitaires
├── config/
│   └── config.json      # Paramètres modifiables (JSON/YAML)
├── audio/
│   ├── annonces/        # Fichiers MP3 d’accueil, bip et erreurs
│   └── enregistrements/ # WAV/MP3 générés
└── logs/                # Fichiers de journalisation
```

---

## Branchements

### 1. Hook switch (combiné Socotel)
- **GPIO BCM 17** (pin 11) connecté à une borne de l’interrupteur hook.
- L’autre borne de l’interrupteur reliée au **3.3 V** (pin 1).
- Activation du pull‑down interne sur GPIO 17 pour garantir LOW quand raccroché.

### 2. Circuit audio (dongle USB)
- **Sortie casque** (Headphone Out) prise jack → fil **speaker** du combiné.
- **Entrée micro** (Mic In) du dongle USB → fil **microphone** du combiné.
- **Masse** du dongle USB → fil **masse** du combiné (commune aux deux signaux).

### 3. Clé USB
- Branchée sur un port USB du Raspberry Pi.
- Point de montage configurable (ex : `/mnt/usb`).

### 4. Alimentation
- **Raspberry Pi 4** alimenté en 5 V (via adaptateur USB‑C ou batterie externe).

---

## Utilisation

- **Monitoring console** : supervision directe via les logs `stdout`.
- **Fichiers générés** :
  - Enregistrements → `audio/enregistrements/`
  - Logs système → `logs/system.log`
- **Paramètres** : modifier `config/config.json` sur la clé et redémarrer le service.

---

## Contribuer

- **Branches** : `main` (stable), `dev` (intégration), `feature/<nom>`.
- **Commits sémantiques** : `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- **Tests** : ajout de tests unitaires pour chaque module avec pytest.

---

## Licence

Licence **GNU GPL v3**. Voir le fichier `LICENSE` pour plus de détails.
