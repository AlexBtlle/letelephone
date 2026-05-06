# Livre d'Or Audio

Un **système de livre d'or audio** sur Raspberry Pi pour les mariages et événements. Les invités décrochent un combiné téléphonique vintage, entendent le message d'accueil du couple, puis enregistrent leur message vocal. Les fichiers sont sauvegardés sur une clé USB et livrés au couple via un lien de téléchargement.

---

## Fonctionnalités

- **Détection du combiné** : hook switch GPIO, décrochage/raccrochage détectés automatiquement
- **Message d'accueil personnalisé** : la voix du couple, configurée avant l'événement
- **Enregistrement automatique** : démarre après l'annonce, s'arrête au raccrochage
- **Durée maximale** : configurable (défaut 3 minutes)
- **Sauvegarde sur clé USB** : enregistrements stockés sur la clé du client, fallback local si absente
- **Son d'erreur** : le combiné indique une panne par un bip si le système ne peut pas enregistrer
- **Démarrage autonome** : service systemd, redémarrage automatique en cas de crash
- **Livraison cloud** : script de mise en ZIP + upload WeTransfer pour envoyer un lien au couple

---

## Architecture

```
letelephone/
├── src/
│   ├── main.py          # Boucle principale
│   ├── config.py        # Chargement de la configuration
│   ├── audio.py         # Lecture / enregistrement (auto-détection ALSA)
│   ├── hook.py          # Détection hook switch (GPIO)
│   ├── storage.py       # Gestion des chemins d'enregistrement
│   ├── usb.py           # Détection et gestion de la clé USB
│   └── selftest.py      # Contrôles au démarrage
├── config/
│   ├── config.default.json   # Paramètres par défaut
│   └── config.event.json     # Surcharge par événement (généré par prepare_event.py)
├── assets/
│   ├── beep.wav              # Son d'accueil par défaut
│   └── error.wav             # Son d'erreur
├── scripts/
│   ├── prepare_event.py      # Prépare un événement (message custom + config)
│   └── retrieve_and_upload.py # Zippe et livre les enregistrements
├── systemd/
│   └── letelephone.service   # Service systemd
├── tests/                    # Tests pytest
├── install.sh                # Script d'installation
└── pyproject.toml
```

---

## Branchements

### Hook switch (combiné Socotel S63 ou similaire)
- **GPIO BCM 17** (pin physique 11) → une borne de l'interrupteur hook
- GND (pin physique 9) → l'autre borne

### Circuit audio (dongle USB)
- **Sortie casque** du dongle → fil **speaker** du combiné
- **Entrée micro** du dongle → fil **microphone** du combiné
- **Masse** du dongle → fil **masse** du combiné

### Alimentation
- Raspberry Pi Zero 2 W ou Pi 4, alimenté en 5 V via l'alimentation officielle

---

## Installation

### Pré-requis

- Raspberry Pi avec Raspberry Pi OS (Lite recommandé)
- Connexion internet au moment de l'installation
- Dongle audio USB branché

### Installation en une commande

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
sudo bash install.sh
```

Le script installe automatiquement :
- Les dépendances système (`python3`, `alsa-utils`, `ffmpeg`)
- Le paquet Python et ses dépendances
- Le service systemd (activé au démarrage)
- Les dossiers `recordings/` et `logs/`

### Démarrer le service

```bash
sudo systemctl start letelephone
sudo systemctl status letelephone
```

### Consulter les logs

```bash
journalctl -u letelephone -f
# ou
cat logs/letelephone.log
```

---

## Utilisation

### Avant l'événement — préparer la personnalisation

Envoie le message d'accueil enregistré par le couple (n'importe quel format : m4a, mp3, wav…) sur le Pi, puis lance :

```bash
python3 scripts/prepare_event.py "Alice & Bob" 2026-06-15 /chemin/vers/welcome.m4a
sudo systemctl restart letelephone
```

Cela convertit le fichier audio en WAV et génère `config/config.event.json`.  
Sans fichier audio, un bip standard est utilisé :

```bash
python3 scripts/prepare_event.py "Alice & Bob" 2026-06-15
```

### Pendant l'événement

1. Brancher la clé USB du client dans le Pi → les enregistrements s'y sauvegardent automatiquement
2. Tester : décrocher → bip/message → enregistrer quelques secondes → raccrocher
3. Vérifier que le fichier apparaît sur la clé

### Après l'événement — livrer les enregistrements

```bash
# Avec clé API WeTransfer (https://developers.wetransfer.com)
WETRANSFER_API_KEY=ton_api_key python3 scripts/retrieve_and_upload.py

# Sans clé API : crée seulement le ZIP
python3 scripts/retrieve_and_upload.py --no-upload
```

Le script produit un ZIP horodaté et envoie un lien de téléchargement au couple.

### Configuration avancée

Modifier `config/config.default.json` pour changer les paramètres globaux :

```json
{
  "hook_pin": 17,
  "poll_interval_sec": 0.05,
  "pre_beep_delay_sec": 2.0,
  "max_duration_sec": 180,
  "audio": { "sample_rate": 44100, "channels": 1 }
}
```

---

## Licence

Licence **GNU GPL v3**. Voir `LICENSE` pour plus de détails.
