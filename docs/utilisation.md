# Guide d'utilisation

## Vue d'ensemble du workflow

```
  AVANT                   PENDANT               APRÈS
  ─────                   ───────               ─────
  Préparer la clé USB  →  Brancher la clé    →  Récupérer la clé
  (welcome.wav,           Allumer le Pi          Copier les fichiers
   couple.txt)            Invités utilisent       ZIP + WeTransfer
                          le téléphone            → couple
```

---

## Avant l'événement

### 1. Préparer la clé USB

Deux fichiers peuvent être placés à la **racine** de la clé USB :

| Fichier | Contenu | Obligatoire |
|---|---|---|
| `welcome.wav` | Message d'accueil enregistré par le couple | Non — bip par défaut |
| `couple.txt` | Nom du couple (ex : `Alice & Bob`) | Non — écran vide sinon |

**Structure de la clé USB avant l'événement :**
```
CLÉUSB/
├── welcome.wav    ← message d'accueil
└── couple.txt     ← "Alice & Bob"
```

**Structure après l'événement :**
```
CLÉUSB/
├── welcome.wav
├── couple.txt
├── enregistrements/
│   ├── message_2026-06-15_14-32-01.wav
│   ├── message_2026-06-15_14-45-18.wav
│   └── ...
└── logs/
    └── letelephone.log
```

---

### 2. Préparer le message d'accueil

Enregistrer le message d'accueil sur téléphone, application vocale, ou micro, puis le convertir au format attendu.

**Format requis :** WAV, mono, 44 100 Hz

Conversion depuis n'importe quel format avec ffmpeg :

```bash
# Sur ton ordinateur (Mac, Linux, Windows avec WSL)
ffmpeg -i welcome.m4a -ar 44100 -ac 1 welcome.wav
```

Outils alternatifs :
- **Audacity** (gratuit) : Fichier → Exporter → WAV, 44 100 Hz, Mono
- **GarageBand** (Mac) : Partager → Exporter le morceau → WAV

Transférer ensuite `welcome.wav` à la racine de la clé USB.

---

### 3. Créer le fichier couple.txt

Créer un fichier texte nommé `couple.txt` contenant uniquement le nom du couple :

```
Alice & Bob
```

Le texte est affiché en permanence sur l'écran OLED. Maximum 20 caractères (le texte est tronqué au-delà).

---

### 4. Tester avant l'événement

Brancher la clé USB, allumer le Pi, et attendre ~30 secondes.

L'écran OLED doit afficher :
```
┌────────────────────────┐
│ Alice & Bob            │
│                        │
│ EN ATTENTE             │
│                        │
│ Messages : 0           │
└────────────────────────┘
```

Simuler un message : décrocher → bip → parler → raccrocher.  
Vérifier que `message_*.wav` est apparu dans `enregistrements/` sur la clé.

---

## Pendant l'événement

### Mise en place

1. Brancher la clé USB préparée dans le port USB du Pi
2. Alimenter le Pi (le démarrage prend ~30 secondes)
3. Vérifier que l'écran affiche le nom du couple et "EN ATTENTE"
4. Placer le téléphone dans un endroit visible et accessible

### Ce que voient les invités

```
  Combiné posé                   Combiné décroché
  ┌──────────────────────┐       ┌──────────────────────┐
  │ Alice & Bob          │       │ Alice & Bob          │
  │                      │       │                      │
  │ EN ATTENTE           │  →    │ * ENREGISTREMENT     │
  │                      │       │                      │
  │ Messages : 3         │       │ Messages : 3         │
  └──────────────────────┘       └──────────────────────┘
```

### Déroulement d'un message

1. L'invité **décroche** le combiné
2. Après 2 secondes : le **message d'accueil** se joue (voix du couple ou bip)
3. L'écran passe en mode **ENREGISTREMENT**
4. L'invité **parle** (durée max : 3 minutes par défaut)
5. L'invité **raccroche** → l'enregistrement est sauvegardé sur la clé USB
6. Le compteur de messages s'incrémente

> Si l'invité raccroche dans la première seconde (accidentellement), le fichier est ignoré automatiquement et le compteur ne change pas.

### Deux personnes en même temps ?

Le téléphone ne gère qu'un message à la fois. Si quelqu'un décroche pendant qu'un message est en cours, il faut qu'il attende que le combiné soit raccroché pour que le système soit à nouveau disponible.

---

## Après l'événement

### 1. Récupérer la clé USB

Éteindre proprement le Pi avant de retirer la clé :

```bash
sudo shutdown now
```

Attendre que la LED rouge s'éteigne, puis retirer la clé.

### 2. Récupérer les enregistrements

Brancher la clé sur un ordinateur. Les fichiers sont dans `enregistrements/`.

### 3. Préparer la livraison

Créer un ZIP du dossier :

**Mac / Linux :**
```bash
zip -r messages_alice_bob.zip enregistrements/
```

**Windows :** clic droit sur le dossier → Compresser dans un fichier ZIP

### 4. Envoyer au couple

Via [WeTransfer](https://wetransfer.com) (gratuit jusqu'à 2 Go) :
1. Aller sur wetransfer.com
2. Glisser le ZIP
3. Entrer l'adresse email du couple
4. Envoyer

---

## Gestion pour plusieurs événements

Le téléphone est conçu pour être réutilisé. Pour passer à un nouvel événement :

1. Brancher la clé USB sur un ordinateur
2. Copier et archiver le dossier `enregistrements/` de l'événement précédent
3. Supprimer le dossier `enregistrements/` de la clé
4. Remplacer `welcome.wav` et `couple.txt` par ceux du nouvel événement
5. La clé est prête pour le prochain événement

Le compteur de messages repart de zéro automatiquement au démarrage (il compte les fichiers présents dans `enregistrements/`).

---

## Dépannage

### Le téléphone ne répond pas au décrochage

1. Vérifier que le service tourne : `sudo systemctl status letelephone`
2. Vérifier le câblage du hook switch avec un multimètre (continuité)
3. Consulter les logs : `journalctl -u letelephone -f`

### Aucun son lors du décrochage

1. Vérifier que le dongle USB est bien reconnu : `aplay -l`
2. Vérifier que `assets/beep.wav` existe
3. Tester manuellement : `aplay -D default assets/beep.wav`

### Le microphone n'enregistre rien

1. Vérifier le câblage micro
2. Tester l'enregistrement : `arecord -D default -f S16_LE -r 44100 -c 1 -d 3 test.wav`
3. Si rien : le microphone à charbon du S63 est peut-être incompatible avec le dongle — voir [remplacement de l'insert microphone](cablage.md#note-sur-le-microphone-à-charbon)

### L'écran OLED ne s'allume pas

1. Vérifier que I2C est activé : `i2cdetect -y 1`
2. Vérifier le câblage (VCC, GND, SDA, SCL)
3. Le logiciel fonctionne sans écran — ce n'est pas bloquant

### Les fichiers ne s'enregistrent pas sur la clé USB

1. Vérifier que la clé est bien montée : `ls /media/pi/`
2. Vérifier les logs : les enregistrements tombent en fallback local (`recordings/`) si la clé est absente
