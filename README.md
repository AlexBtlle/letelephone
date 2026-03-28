# Livre d’Or Audio

**En cours de développement - Je ne garantie pas le bon fonctionnement**

Un **système interactif de livre d’or audio** basé sur Raspberry Pi permettant de recueillir des messages vocaux lors d’un événement (par exemple, un mariage). Les invités décrochent un combiné de téléphone ancien, entendent une annonce d’accueil, puis enregistrent leur message qui est stocké sur une clé USB.

---

## Fonctionnalités

- **Détection du combiné** : Hook switch (GPIO) détecte le décrochage et le raccrochage.
- **Annonce sonore** : Lecture automatique d’un fichier MP3 d’accueil dès le décrochage.
- **Enregistrement audio** : Démarrage automatique de l’enregistrement après l’annonce, fin lors du raccrochage.
- **Durée maximale** : Timer configurable pour limiter la durée d’enregistrement.
- **Stockage sur clé USB** : Vérification de la présence de la clé, lecture/écriture des enregistrements et des logs sur la partition auto-montée.
- **Configuration dynamique** : Paramètres (GPIO, durées, chemins, chemins d’annonces et erreurs) modifiables via `config.json` sur la clé USB.
- **Journalisation** : Logs d’événements (décrochage, début/arrêt, erreurs) écrits dans `logs/system.log` sur la clé, avec rotation.
- **TODO Démarrage autonome** : Lancement du service Python au boot via systemd (à configurer).

> **Évolutions envisagées** : Interface Web pour consulter et écouter les messages à distance.

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
│   ├── utils.py         # Fonctions utilitaires
├── config/
│   └── config.json      # Paramètres modifiables sur la clé USB
├── audio/
│   ├── annonces/        # MP3/WAV d’accueil, bip et erreurs
│   └── enregistrements/ # WAV/MP3 générés sur la clé
└── logs/                # (Sur la clé) Logs système
```

---

## Branchements

### 1. Hook switch (combiné Socotel)
- **GPIO BCM 17** (pin 11) connecté à une borne de l’interrupteur hook.
- L’autre borne de l’interrupteur reliée au **3.3 V** (pin 1).
- Activation du pull‑down interne sur GPIO 17 pour garantir LOW quand raccroché.

### 2. Circuit audio (dongle USB)
- **Sortie casque** (Headphone Out) du dongle USB → fil **speaker** du combiné.
- **Entrée micro** (Mic In) du dongle USB → fil **microphone** du combiné.
- **Masse** du dongle USB → fil **masse** du combiné.

### 3. Clé USB
- Auto-montée dans `/media/<user>/<volume>`.
- Contient `config.json`, dossiers `annonces/`, `enregistrements/`, `logs/`.

### 4. Alimentation
- **Raspberry Pi 4** alimenté en 5 V (via adaptateur USB‑C ou batterie externe).

---

## Installation & Déploiement

1. Créer le dépôt sur GitHub, cloner et ouvrir localement.
2. Créer un environnement virtuel (non obligatoire)
3. Préparer la clé USB :
   - Copier `config.json`, `annonces/` et créer dossiers `enregistrements/` et `logs/`.
   - Brancher la clé sur le Pi.

---

## Utilisation

- **Monitoring console** : logs en direct.
- **Fichiers** :
  - Enregistrements → `annonces/` et `enregistrements/` sur la clé.
  - Logs → `logs/system.log` sur la clé.
- **Paramètres** : éditer `config.json` sur la clé et redémarrer le service.

---

## Contribuer

- **Branches** : `main`, `dev`, `feature/<nom>`.
- **Commits sémantiques** : `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- **Tests** : unités via pytest pour chaque module.

---

## Licence

Licence **GNU GPL v3**. Voir `LICENSE` pour plus de détails.

> **Note**: Certaines parties du contenu de ce projet (code, documentation, README) ont été générées par ChatGPT.
