# Guide d'utilisation

Ce guide est destiné à la personne qui loue ou utilise le téléphone pour un événement. Pas besoin de connaissances techniques.

---

## Vue d'ensemble

```
  AVANT L'ÉVÉNEMENT       PENDANT          APRÈS
  ─────────────────       ───────          ─────
  Préparer la clé USB  →  Brancher la    → Récupérer la clé USB
  Enregistrer le          clé + allumer  → Envoyer les fichiers
  message d'accueil       le Pi            au couple
```

---

## Avant l'événement

### 1. Préparer la clé USB

Deux fichiers peuvent être placés à la **racine** de la clé USB (pas dans un sous-dossier) :

| Fichier | Rôle | Obligatoire ? |
|---|---|---|
| `welcome.wav` | Le message d'accueil que les invités entendent en décrochant | Non — un bip retentit par défaut |
| `couple.txt` | Le nom du couple affiché en permanence sur l'écran | Non — l'écran est vide sinon |

**Structure de la clé avant l'événement :**
```
MA-CLÉ-USB/
├── welcome.wav     ← message d'accueil du couple
└── couple.txt      ← "Alice & Bob"
```

---

### 2. Enregistrer le message d'accueil

Le message d'accueil est ce que les invités entendent dès qu'ils décrochent, avant de pouvoir parler. C'est typiquement : *"Bonjour, c'est Alice et Bob. Laissez-nous un petit message, on sera ravis de l'écouter !"*

**Enregistrer le message :**
- Sur smartphone : l'application Mémo Vocal (iPhone) ou Enregistreur vocal (Android) fait très bien l'affaire
- Sur ordinateur : n'importe quel logiciel d'enregistrement (Audacity, QuickTime sur Mac…)

**Convertir au bon format (WAV, mono, 44 100 Hz) :**

Le format WAV est indispensable. La conversion se fait en une commande si ffmpeg est installé :

```bash
# Sur Mac/Linux (Terminal) ou Windows (invite de commandes avec ffmpeg installé)
ffmpeg -i welcome.m4a -ar 44100 -ac 1 welcome.wav
ffmpeg -i welcome.mp3 -ar 44100 -ac 1 welcome.wav
```

Alternative sans ligne de commande :
- **Audacity** (gratuit, Mac/Windows/Linux) : ouvrir le fichier → Fichier → Exporter → Exporter en WAV → Format : WAV PCM, 44 100 Hz, Mono

Copier le fichier `welcome.wav` obtenu à la racine de la clé USB.

---

### 3. Créer le fichier couple.txt

Créer un fichier texte (Bloc-notes sur Windows, TextEdit sur Mac) contenant uniquement le nom du couple, enregistrer sous le nom exact `couple.txt`, et le copier à la racine de la clé USB.

```
Alice & Bob
```

> Maximum 20 caractères — le texte est coupé s'il dépasse.

---

### 4. Tester avant l'événement

Faire un test complet la veille, pas le jour J.

1. Brancher la clé USB préparée
2. Allumer le Pi (attendre ~30 secondes)
3. L'écran doit afficher le nom du couple et "EN ATTENTE"
4. Décrocher → attendre le message d'accueil → parler quelques mots → raccrocher
5. Vérifier que le dossier `enregistrements/` est apparu sur la clé avec un fichier `message_*.mp3` dedans
6. Écouter le fichier depuis un ordinateur pour vérifier la qualité

---

## Pendant l'événement

### Mise en place

1. Brancher la clé USB préparée dans le port USB du Pi
2. Brancher l'alimentation (attendre ~30 secondes — le démarrage est silencieux)
3. Vérifier que l'écran affiche le nom du couple et "EN ATTENTE"
4. Poser le téléphone bien en évidence, avec un petit mot explicatif pour les invités

---

### Ce que voient les invités

```
  Combiné posé                      Combiné décroché
  ┌──────────────────────┐          ┌──────────────────────┐
  │ Alice & Bob          │          │ Alice & Bob          │
  │                      │  →décroche→                    │
  │ EN ATTENTE           │          │ * ENREGISTREMENT     │
  │                      │          │                      │
  │ Messages : 3         │          │ Messages : 3         │
  └──────────────────────┘          └──────────────────────┘
```

---

### Déroulement d'un message

1. L'invité **décroche** le combiné
2. Après ~2 secondes : le **message d'accueil** du couple se joue
3. L'écran passe en mode **\* ENREGISTREMENT**
4. L'invité **parle** (durée maximale : 3 minutes par défaut)
5. L'invité **raccroche** → le message est automatiquement sauvegardé sur la clé USB
6. Le compteur de messages s'incrémente sur l'écran

> Si quelqu'un raccroche dans la première seconde (par accident), le fichier est ignoré et le compteur ne change pas.

---

### Deux invités en même temps ?

Le téléphone enregistre un message à la fois. Si quelqu'un décroche pendant qu'un message est en cours, il faut qu'il attende que le premier invité ait raccroché.

---

## Après l'événement

### 1. Éteindre proprement le Pi

**Option A — Bouton d'arrêt (si installé) :**
Maintenir le bouton enfoncé pendant 3 secondes. Un bip de confirmation retentit, le Pi s'éteint.

**Option B — Via SSH :**
```bash
ssh pi@letelephone.local
sudo shutdown now
```

**Option C — En coupant l'alimentation (déconseillé) :**
En dernier recours seulement. Attendre que le voyant rouge du Pi soit éteint avant de débrancher, sinon les fichiers sur la clé USB risquent d'être corrompus.

---

### 2. Récupérer les fichiers

Brancher la clé USB sur un ordinateur. Le dossier `enregistrements/` contient tous les messages au format MP3 :

```
MA-CLÉ-USB/
├── welcome.wav
├── couple.txt
└── enregistrements/
    ├── message_2026-06-15_14-32-01.mp3
    ├── message_2026-06-15_14-45-18.mp3
    └── ...
```

Les fichiers MP3 sont compatibles avec tous les lecteurs (téléphone, ordinateur, tablette). Ils sont automatiquement normalisés (volume équilibré) et compressés — chaque fichier pèse environ 1–3 Mo.

---

### 3. Envoyer les messages au couple

**Créer un ZIP du dossier :**

Sur Mac/Linux :
```bash
zip -r messages_alice_bob.zip enregistrements/
```
Sur Windows : clic droit sur le dossier `enregistrements/` → *Compresser dans un fichier ZIP*

**Envoyer via WeTransfer** (gratuit jusqu'à 2 Go) :
1. Aller sur [wetransfer.com](https://wetransfer.com)
2. Glisser le fichier ZIP
3. Saisir l'adresse email du couple
4. Envoyer

---

## Préparer le téléphone pour un nouvel événement

Le téléphone est conçu pour être utilisé autant de fois que tu veux. Pour passer à un nouvel événement :

1. Brancher la clé USB sur un ordinateur
2. Copier le dossier `enregistrements/` ailleurs (sauvegarde de l'événement précédent)
3. Supprimer le dossier `enregistrements/` de la clé
4. Remplacer `welcome.wav` et `couple.txt` par ceux du nouvel événement
5. La clé est prête

Le compteur de messages repart automatiquement de zéro au démarrage suivant.

---

## Dépannage

### Le téléphone ne réagit pas quand on décroche

1. Vérifier que le Pi est bien allumé (voyant rouge allumé)
2. Vérifier que le service tourne :
   ```bash
   sudo systemctl status letelephone
   ```
3. Si le service est arrêté, regarder pourquoi :
   ```bash
   journalctl -u letelephone -n 50
   ```
4. Vérifier le câblage du hook switch avec un multimètre (mode continuité) — combiné posé = bip, soulevé = silence

---

### Aucun son quand on décroche (pas de bip, pas de message d'accueil)

1. Vérifier que le dongle USB (ou le Codec Zero) est bien branché
2. Vérifier qu'il est reconnu par le Pi :
   ```bash
   aplay -l
   ```
   → doit afficher une ligne avec `USB Audio` ou `IQaudIO`
3. Tester manuellement :
   ```bash
   aplay assets/beep.wav
   ```
4. Si le fichier `welcome.wav` est sur la clé et n'est pas lu, vérifier le format (WAV, mono, 44 100 Hz)

---

### Le microphone n'enregistre rien (fichier vide ou silencieux)

1. Vérifier le câblage des fils du micro
2. Tester l'enregistrement manuellement :
   ```bash
   arecord -f S16_LE -r 44100 -c 1 -d 5 test.wav && aplay test.wav
   ```
3. Si le fichier est vide ou très faible : le microphone à charbon d'origine du S63 est peut-être incompatible avec le dongle ou le Codec Zero. Solution : remplacer l'insert microphone par un insert électret (2–5 €, voir [guide de câblage](cablage.md))

---

### L'écran OLED ne s'allume pas

Ce n'est pas bloquant — le système fonctionne parfaitement sans écran. Si tu veux quand même le faire fonctionner :
1. Vérifier que I2C est activé : `i2cdetect -y 1` → doit afficher `3c`
2. Vérifier le câblage (VCC, GND, SDA, SCL)
3. Certains modules ont VCC et GND inversés sur le connecteur — vérifier le marquage

---

### Les fichiers ne s'enregistrent pas sur la clé USB

Les messages sont sauvegardés localement sur le Pi si la clé est absente ou non reconnue. Pour les récupérer :
```bash
ls letelephone/recordings/
```
Vérifier les logs pour comprendre pourquoi la clé n'est pas utilisée :
```bash
journalctl -u letelephone | grep USB
```

---

### Sur Pi Zero 2 W : le service ne démarre pas et parle de "Codec Zero"

Le pilote audio n'est pas activé. Vérifier que `dtoverlay=iqaudio-codec` est bien dans `/boot/firmware/config.txt` et redémarrer :
```bash
grep iqaudio /boot/firmware/config.txt   # doit afficher la ligne
sudo reboot
```
Si la ligne n'est pas là, relancer l'installation :
```bash
cd letelephone && sudo bash install.sh
```
