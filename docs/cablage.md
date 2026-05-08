# Guide de câblage

Ce guide couvre les deux configurations : dongle USB (Pi 3B+/4/5) et IQaudio Codec Zero (Pi Zero 2 W).

---

## Vue d'ensemble

```
  ┌──────────────────────────────────────────────────────────────┐
  │                        Raspberry Pi                          │
  │                                                              │
  │   GPIO 17  ──────────────────────── Hook switch             │
  │   GPIO 2   ──────────────────────── OLED SDA (optionnel)    │
  │   GPIO 3   ──────────────────────── OLED SCL (optionnel)    │
  │   GPIO 27  ──────────────────────── Bouton arrêt (optionnel)│
  │   3.3V     ──────────────────────── OLED VCC (optionnel)    │
  │   GND      ──────────────────────── OLED GND (optionnel)    │
  │                                                              │
  │   USB-A    ──── Dongle audio  ──── Combiné (config standard)│
  │   USB-A    ──── Clé USB                                     │
  │                                                              │
  │   [HAT GPIO] ── Codec Zero ──── Combiné (config compacte)   │
  └──────────────────────────────────────────────────────────────┘
```

---

## 1. Le hook switch (tous les modèles)

Le hook switch est le petit interrupteur sous l'emplacement du combiné. Quand le combiné est posé, il est appuyé (circuit fermé). Quand on décroche, il se relève (circuit ouvert).

**Principe :**

```
  Combiné posé (raccroché)        Combiné décroché
  ┌────────────────────────┐      ┌────────────────────────┐
  │  Switch FERMÉ          │      │  Switch OUVERT         │
  │  GPIO 17 ←──────── GND │      │  GPIO 17  (en l'air)   │
  └────────────────────────┘      └────────────────────────┘
  → "en attente"                  → "enregistrement"
```

> Pas de résistance externe à ajouter. Le Pi active une résistance interne (pull-up) qui maintient le signal à 3,3 V quand le switch est ouvert.

**Câblage :**

```
  Raspberry Pi                 Hook switch (Socotel S63)
  Pin 11  (GPIO 17) ────────── Borne A ─┐
                                         │  (interrupteur)
  Pin  9  (GND)     ────────── Borne B ─┘
```

**Localiser le hook switch dans le S63 :**

```
  Vue de dessous du Socotel S63 (boîtier retourné, couvercle enlevé)
  ┌────────────────────────────────────────────────┐
  │                                                │
  │   [Cadran rotatif]            [Hook switch]    │
  │                                ┌──────────┐    │
  │                                │ NC  A  B │    │
  │                                └──────────┘    │
  │                                                │
  └────────────────────────────────────────────────┘

  NC = Normalement Fermé (le circuit est fermé quand personne n'appuie)
  A et B = les deux bornes à câbler
```

**Comment confirmer les bonnes bornes avec un multimètre :**
1. Mettre le multimètre en mode continuité (symbole diode ou bip)
2. Poser les pointes sur A et B
3. Combiné posé → bip (circuit fermé) ✓
4. Combiné soulevé → silence (circuit ouvert) ✓

---

## 2a. Connexion audio — Dongle USB (Pi 3B+/4/5)

Le Socotel S63 a un câble spiralé à **4 fils** entre le combiné et le boîtier. Deux fils vont à l'écouteur, deux au microphone.

**Identifier les fils :**

Ouvrir le boîtier du S63 (3 vis sous la base), localiser le câble spiralé, et tester chaque paire avec le multimètre en mode résistance (Ω) :

```
  Paire écouteur  → résistance entre 100 Ω et 300 Ω (stable)
  Paire micro     → résistance entre 50 Ω et 200 Ω (variable si on souffle)
```

> Les couleurs varient selon l'année de fabrication. Ne pas se fier aux couleurs — toujours vérifier avec le multimètre.

**Câblage vers le dongle audio USB :**

La plupart des dongles ont deux prises jack 3,5 mm séparées (une verte pour l'écouteur, une rose pour le micro) :

```
  Dongle audio USB                 Combiné Socotel S63
  ┌─────────────────┐
  │  Jack vert (HP) │
  │  Tip  ──────────┼──────────── Écouteur (fil +)
  │  Sleeve ────────┼──────────── Écouteur (fil −)
  │                 │
  │  Jack rose (MIC)│
  │  Tip  ──────────┼──────────── Microphone (fil +)
  │  Sleeve ────────┼──────────── Microphone (fil −)
  └─────────────────┘
```

> Sleeve = la bague métallique tout au bout de la fiche jack (la masse/GND).

**Si le dongle n'a qu'un seul jack TRRS (comme sur certains PC portables) :**

```
  TRRS (de la pointe vers la base)
  ├── Tip    (T) ──── Écouteur (+)
  ├── Ring 1 (R) ──── (relier à Tip ou laisser libre)
  ├── Ring 2 (R) ──── Microphone (+)
  └── Sleeve (S) ──── Écouteur (−) et Microphone (−) reliés ensemble
```

---

## 2b. Connexion audio — IQaudio Codec Zero (Pi Zero 2 W)

Le Codec Zero est un HAT (carte d'extension) qui s'emboîte directement sur les broches GPIO du Pi Zero 2 W. Pas de soudure, pas de dongle USB.

**Installation physique :**

```
  Pi Zero 2 W (vu de profil)
  ┌──────────────────────────────────┐
  │                                  │
  │  [●●●●●●●●●●●●●●●●●●●●] GPIO    │
  └──────────────────────────────────┘
                    ↑
             emboîter ici
                    ↓
  ┌──────────────────────────────────┐
  │  IQaudio Codec Zero              │
  │  [Jack TRRS 3,5mm] ──── Combiné │
  └──────────────────────────────────┘
```

Le Codec Zero dispose d'un unique jack TRRS 3,5 mm (comme les écouteurs de smartphone avec micro). Le combiné se branche sur ce jack.

**Câblage du combiné vers le jack TRRS du Codec Zero :**

```
  Jack TRRS Codec Zero (de la pointe vers la base)
  ├── Tip    (T) ──── Écouteur (+)
  ├── Ring 1 (R) ──── Microphone (+)
  ├── Ring 2 (R) ──── (masse micro — relier à Sleeve)
  └── Sleeve (S) ──── Écouteur (−) et Microphone (−) reliés ensemble
```

Utiliser une fiche jack TRRS 3,5 mm à souder (disponible sur AliExpress pour quelques centimes).

**Note sur le microphone :**
Le Codec Zero fournit une alimentation micro compatible avec les inserts électret mais **pas** avec le microphone à charbon d'origine du S63. Si le son capté est faible ou absent : remplacer l'insert microphone par un insert à électret (2–5 € sur AliExpress, recherche : "telephone electret insert").

---

## 3. Écran OLED SSD1306 (optionnel, tous modèles)

L'écran communique via le bus I2C. Le câblage est identique sur tous les Pi.

```
  OLED SSD1306 128×64          Raspberry Pi
  ┌───────────┐
  │ VCC ──────┼──────────────── 3,3 V  (Pin 1)
  │ GND ──────┼──────────────── GND    (Pin 6)
  │ SDA ──────┼──────────────── GPIO 2 (Pin 3)
  │ SCL ──────┼──────────────── GPIO 3 (Pin 5)
  └───────────┘
```

> Certains modules SSD1306 ont VCC et GND inversés. Vérifier le marquage sur le circuit imprimé avant de brancher.

**Activer le bus I2C sur le Pi :**
```bash
sudo raspi-config
# Interface Options → I2C → Enable → Finish
sudo reboot
```

**Vérifier que l'écran est détecté :**
```bash
sudo apt install i2c-tools
i2cdetect -y 1
# L'adresse 3c doit apparaître dans la grille
```

---

## 4. Bouton d'arrêt (optionnel, tous modèles)

Un bouton-poussoir ordinaire. Un appui maintenu 3 secondes éteint proprement le Pi. Idéal pour les non-techniciens en fin de soirée — plus besoin de taper une commande.

**Câblage :**

```
  Raspberry Pi                 Bouton poussoir
  Pin 13  (GPIO 27) ────────── Borne A ─┐
                                         │  (bouton momentané)
  Pin 14  (GND)     ────────── Borne B ─┘
```

> N'importe quel bouton-poussoir momentané fait l'affaire (NO = Normalement Ouvert). Prix : 1–2 € sur AliExpress ou Conrad.

**Activer dans la configuration :**

Éditer `config/config.default.json` :
```json
"shutdown_button": {
  "enabled": true,
  "pin": 27,
  "hold_duration_sec": 3.0
}
```

---

## 5. Brochage GPIO de référence

Le connecteur GPIO 40 broches est identique sur Pi 3B+, Pi 4, Pi 5 et Pi Zero 2 W.

```
                         ┌──────────────────────────────┐
                   3,3V  │ (1)  ○  (2) │  5V            │
       SDA / GPIO 2  ●───│ (3)  ○  (4) │  5V            │
       SCL / GPIO 3  ●───│ (5)  ○  (6) │  GND           │
             GPIO 4      │ (7)  ○  (8) │  GPIO 14       │
                GND  ●───│ (9)  ○ (10) │  GPIO 15       │
      HOOK / GPIO 17 ●───│(11)  ○ (12) │  GPIO 18       │
   BOUTON / GPIO 27  ●───│(13)  ○ (14) │  GND  ●────────┤ (bouton arrêt)
             GPIO 22     │(15)  ○ (16) │  GPIO 23       │
                3,3V ●───│(17)  ○ (18) │  GPIO 24       │
             GPIO 10     │(19)  ○ (20) │  GND           │
              GPIO 9     │(21)  ○ (22) │  GPIO 25       │
             GPIO 11     │(23)  ○ (24) │  GPIO 8        │
                GND      │(25)  ○ (26) │  GPIO 7        │
                         └──────────────────────────────┘

  Pins utilisés :
  ●  (1) 3,3V    → OLED VCC
  ●  (3) GPIO 2  → OLED SDA
  ●  (5) GPIO 3  → OLED SCL
  ●  (9) GND     → Hook switch (borne B)
  ● (11) GPIO 17 → Hook switch (borne A)
  ● (13) GPIO 27 → Bouton arrêt (borne A)
  ● (14) GND     → Bouton arrêt (borne B)
```

---

## 6. Schéma complet — Configuration standard

```
  ┌────────────────────────────────────────────────────────────────┐
  │                      Raspberry Pi 3B+/4/5                      │
  │                                                                │
  │  Pin  1 (3,3V) ────────────────────────────── OLED VCC        │
  │  Pin  3 (SDA)  ────────────────────────────── OLED SDA        │
  │  Pin  5 (SCL)  ────────────────────────────── OLED SCL        │
  │  Pin  6 (GND)  ────────────────────────────── OLED GND        │
  │  Pin  9 (GND)  ──────┐                                        │
  │  Pin 11 (GPIO17)─────┘──── [Hook switch S63]                  │
  │  Pin 13 (GPIO27)─────┐                                        │
  │  Pin 14 (GND)  ──────┘──── [Bouton arrêt]                     │
  │                                                                │
  │  [USB-A] ──── Dongle audio USB ──── Écouteur + Micro combiné  │
  │  [USB-A] ──── Clé USB                                         │
  │  [PWR]   ──── Alimentation 5V                                 │
  └────────────────────────────────────────────────────────────────┘
                                     │
                               ┌─────┴──────────────────┐
                               │     OLED SSD1306        │
                               └────────────────────────┘
```

## 7. Schéma complet — Configuration compacte (Pi Zero 2 W)

```
  ┌──────────────────────────────────────────────────────┐
  │                    Pi Zero 2 W                       │
  │  Pin  9 (GND)   ──────┐                              │
  │  Pin 11 (GPIO17)──────┘──── [Hook switch S63]        │
  │  Pin 13 (GPIO27)──────┐                              │
  │  Pin 14 (GND)   ──────┘──── [Bouton arrêt]           │
  │                                                      │
  │  [HAT GPIO 40 broches] ──────────────────────────┐   │
  └──────────────────────────────────────────────────┼───┘
                                                     │
  ┌──────────────────────────────────────────────────┘
  │  IQaudio Codec Zero HAT
  │  [Jack TRRS 3,5mm] ──── Écouteur + Micro combiné S63
  └───────────────────────────────────────────────────────
```

---

## Conseils de montage

- Utiliser de la gaine thermorétractable sur chaque connexion soudée (chauffer avec un briquet ou décapeur).
- Fixer le Pi avec des entretoises en plastique M2.5 — évite les courts-circuits avec le boîtier métallique.
- Prévoir un trou dans le boîtier pour le câble d'alimentation et éventuellement la clé USB.
- Le hook switch doit être accessible depuis l'extérieur : le combiné doit appuyer dessus quand il est posé. Tester avec le multimètre avant de refermer le boîtier.
- L'écran OLED peut être collé derrière une découpe dans le boîtier ou glissé dans l'emplacement du cadran si on l'a retiré.
