# Schémas de câblage

## Vue d'ensemble du système

```
                        ┌──────────────────────────────┐
                        │       Raspberry Pi            │
                        │                               │
  ┌─────────────┐       │  GPIO 17 ──── Hook switch     │
  │  Socotel S63│       │  GPIO 2  ──── OLED SDA        │
  │             │       │  GPIO 3  ──── OLED SCL        │
  │  Hook switch├───────┤  3.3V    ──── OLED VCC        │
  │  Earpiece   ├───┐   │  GND     ──── OLED GND        │
  │  Microphone ├───┤   │                               │
  └─────────────┘   │   │  USB ──── Dongle audio ───────┤
                    └───┤  USB ──── Clé USB             │
                        │  USB-C/µUSB ── Alimentation   │
                        └──────────────────────────────┘
                                         │
                                  ┌──────┴──────┐
                                  │  OLED SSD1306│
                                  └─────────────┘
```

---

## 1. Brochage du Raspberry Pi (GPIO)

Le connecteur GPIO est identique sur le Pi Zero 2 W et le Pi 4.  
Les pins utilisés sont indiqués en **gras**.

```
                           ┌─────────────────────────────┐
                     3.3V  │ (1)  (2) │  5V              │
         SDA / GPIO 2  ●───│ (3)  (4) │  5V              │
         SCL / GPIO 3  ●───│ (5)  (6) │  GND             │
               GPIO 4      │ (7)  (8) │  GPIO 14         │
                  GND  ●───│ (9) (10) │  GPIO 15         │
        HOOK / GPIO 17 ●───│(11) (12) │  GPIO 18         │
               GPIO 27     │(13) (14) │  GND             │
               GPIO 22     │(15) (16) │  GPIO 23         │
                  3.3V ●───│(17) (18) │  GPIO 24         │
               GPIO 10     │(19) (20) │  GND             │
               GPIO 9      │(21) (22) │  GPIO 25         │
               GPIO 11     │(23) (24) │  GPIO 8          │
                  GND      │(25) (26) │  GPIO 7          │
                           └─────────────────────────────┘

  Pins utilisés :
  ● (1)  3.3V    → OLED VCC
  ● (3)  GPIO 2  → OLED SDA
  ● (5)  GPIO 3  → OLED SCL
  ● (9)  GND     → Hook switch (borne 2)
  ● (11) GPIO 17 → Hook switch (borne 1)
  ● (17) 3.3V    → (disponible si pin 1 occupé)
```

---

## 2. Hook switch (Socotel S63)

Le hook switch est l'interrupteur actionné par le poids du combiné.  
Chez le S63, il est accessible en ouvrant le boîtier (3 vis sous la base).

**Principe de fonctionnement :**

```
  Combiné posé (raccroché)      Combiné soulevé (décroché)
  ┌──────────────┐              ┌──────────────┐
  │ Switch FERMÉ │              │ Switch OUVERT│
  │  GPIO 17 ←──┤──── GND      │  GPIO 17     │  ← tiré à 3.3V en interne
  └──────────────┘              └──────────────┘
       → is_off_hook() = False       → is_off_hook() = True
```

**Câblage :**

```
  Raspberry Pi                Hook switch (Socotel S63)
  Pin 11 (GPIO 17) ───────────  Borne A  ─┐
                                           │ (interrupteur NC)
  Pin  9 (GND)     ───────────  Borne B  ─┘
```

> Pas de résistance externe nécessaire : la résistance de tirage interne du Pi (pull-up) est activée par le logiciel.

**Localisation du hook switch dans le S63 :**

```
  Vue de dessous du Socotel S63 (boîtier ouvert)

  ┌────────────────────────────────────┐
  │                                    │
  │   [Cadran]          [Hook switch]  │
  │                      ┌──────┐      │
  │                      │  NC  │      │
  │                      │ A  B │      │
  │                      └──────┘      │
  │                                    │
  └────────────────────────────────────┘

  A et B : les deux bornes à câbler vers le Pi
  NC = Normalement Fermé (Normally Closed)
```

> Sur certains S63, le hook switch est accessible directement via deux fils soudés sur le circuit. Utiliser un multimètre en mode continuité pour confirmer : bip = switch fermé (combiné posé).

---

## 3. Dongle audio USB → Combiné

Le Socotel S63 utilise un câble spiralé à **4 fils** entre le combiné et le boîtier.  
Deux fils vont à l'écouteur, deux au microphone.

### Identifier les fils

Ouvrir le boîtier du S63 et localiser les 4 fils du câble spiralé sur la carte interne.

```
  Câble combiné S63 (4 fils typiques)

  ┌────────────────────────────────┐
  │ Fil 1 (ex: rouge)  ─ Écouteur +│
  │ Fil 2 (ex: vert)   ─ Écouteur -│
  │ Fil 3 (ex: jaune)  ─ Micro +   │
  │ Fil 4 (ex: noir)   ─ Micro -   │
  └────────────────────────────────┘
```

> Les couleurs varient selon l'année de fabrication. Utiliser un multimètre pour confirmer :
> - Écouteur : résistance ~100–300 Ω entre les deux fils
> - Microphone (charbon) : résistance ~50–200 Ω, variable selon la pression

### Connexion au dongle audio

```
  Dongle USB audio                Combiné Socotel S63
  ┌────────────────┐
  │                │
  │  [Jack 3.5mm]  │
  │   Sortie (HP)  │
  │   TIP  ────────┼──────────────── Écouteur (+)
  │   SLEEVE ──────┼──────────────── Écouteur (-)
  │                │
  │  [Jack 3.5mm]  │
  │   Entrée (MIC) │
  │   TIP  ────────┼──────────────── Micro (+)
  │   SLEEVE ──────┼──────────────── Micro (-)
  └────────────────┘
```

> **Si le dongle dispose d'un seul jack TRRS combiné (comme sur certains PC portables) :**
> ```
> TRRS : Tip=HP gauche, Ring1=HP droit, Ring2=MIC, Sleeve=GND
>
> TIP   ──── Écouteur (+)
> Ring1 ──── (relier à TIP ou laisser NC)
> Ring2 ──── Micro (+)
> Sleeve──── Écouteur (-) et Micro (-)
> ```

### Note sur le microphone à charbon

Le microphone d'origine du S63 est un **microphone à charbon** qui nécessite une alimentation (tension de polarisation ~3–9 V). Certains dongles USB ne la fournissent pas.

**Symptômes :** son faible ou absent en entrée micro.

**Solution :** remplacer l'insert microphone par un insert électret compatible :

```
  Circuit adaptateur microphone électret

  3.3V ──── 4.7kΩ ────┬──── MIC (+) du dongle
                       │
                    [Insert électret]
                       │
  GND  ───────────────┴──── MIC (-) du dongle
```

Des inserts compatibles S63 sont disponibles sur AliExpress ("telephone electret insert") pour environ 2–5 €.

---

## 4. Écran OLED SSD1306 (optionnel)

L'écran communique via le bus I2C du Pi (adresse 0x3C par défaut).

```
  OLED SSD1306              Raspberry Pi
  ┌──────────┐
  │ VCC ─────┼──────────────── 3.3V   (Pin 1)
  │ GND ─────┼──────────────── GND    (Pin 6)
  │ SDA ─────┼──────────────── GPIO 2 (Pin 3)
  │ SCL ─────┼──────────────── GPIO 3 (Pin 5)
  └──────────┘
```

> Certains modules SSD1306 sont vendus avec l'ordre VCC/GND inversé. Vérifier le marquage sur le module avant de brancher.

**Activer I2C sur le Pi :**
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

**Vérifier la détection :**
```bash
sudo apt install i2c-tools
i2cdetect -y 1
# Doit afficher 3c dans la grille
```

---

## 5. Schéma complet

```
  ┌─────────────────────────────────────────────────────────┐
  │                   Raspberry Pi                          │
  │                                                         │
  │  Pin  1  (3.3V) ──────────────────────── OLED VCC      │
  │  Pin  3  (SDA)  ──────────────────────── OLED SDA      │
  │  Pin  5  (SCL)  ──────────────────────── OLED SCL      │
  │  Pin  6  (GND)  ──────────────────────── OLED GND      │
  │  Pin  9  (GND)  ──────┐                               │
  │  Pin 11  (GPIO17)─────┤                               │
  │                        └── [Hook switch S63]           │
  │                                                         │
  │  [USB] ─────────────── Dongle audio USB ─┐             │
  │  [USB] ─────────────── Clé USB            │             │
  │  [PWR] ─────────────── Alimentation 5V    │             │
  └───────────────────────────────────────────┼─────────────┘
                                              │
                                    ┌─────────┴──────────┐
                                    │  Combiné Socotel S63│
                                    │                     │
                                    │  Écouteur + ── TIP  │  (Jack HP 3.5mm)
                                    │  Écouteur - ──SLEEVE│
                                    │  Micro    + ── TIP  │  (Jack MIC 3.5mm)
                                    │  Micro    - ──SLEEVE│
                                    └─────────────────────┘
```

---

## Conseils de montage

- Utiliser de la gaine thermorétractable sur chaque connexion soudée.
- Fixer le Pi dans le boîtier avec des entretoises M2.5 et des boulons nylon pour éviter les courts-circuits.
- Prévoir un trou dans le boîtier pour le câble USB d'alimentation.
- L'écran OLED peut être collé à l'intérieur du cadran ou dans une découpe faite dans la façade.
- Laisser le hook switch accessible depuis l'extérieur du boîtier (il doit être actionné par le poids du combiné).
