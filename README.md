# Livre d’Or Audio

**En cours de développement - Je ne garantie pas le bon fonctionnement**

Un **système interactif de livre d’or audio** basé sur Raspberry Pi permettant de recueillir des messages vocaux lors d’un événement (par exemple, un mariage). Les invités décrochent un combiné de téléphone ancien, entendent une annonce d’accueil (ou juste un bip), puis enregistrent leur message qui est stocké sur le Raspberry Pi.

---

## Fonctionnalités

- **Détection du combiné** : Hook switch (GPIO) détecte le décrochage et le raccrochage.
- **Annonce sonore** : Lecture automatique d’un fichier WAV beep.wav.
- **Enregistrement audio** : Démarrage automatique de l’enregistrement après l’annonce, fin lors du raccrochage.
- **Durée maximale** : TODO
- **TODO Démarrage autonome** : TODO

> **Évolutions envisagées** : Enregistrement sur une clé USB. Paramètrage via un fichier stocké sur la clé.

---

## Architecture du projet

```

```

---

## Branchements

### 1. Hook switch (combiné Socotel)
- **GPIO BCM 17** (pin 11) connecté à une borne de l’interrupteur hook.
- L’autre borne de l’interrupteur reliée au GND.

### 2. Circuit audio (dongle USB)
- **Sortie casque** (Headphone Out) du dongle USB → fil **speaker** du combiné.
- **Entrée micro** (Mic In) du dongle USB → fil **microphone** du combiné.
- **Masse** du dongle USB → fil **masse** du combiné.

### 4. Alimentation
- **Raspberry Pi 4** alimenté en 5 V (Je recommande l'utilisation de l'alimentation officielle).

---

## Installation & Déploiement

1. Créer le dépôt sur GitHub, cloner et ouvrir localement.

---

## Utilisation


---

## Contribuer

---

## Licence

Licence **GNU GPL v3**. Voir `LICENSE` pour plus de détails.

> **Note**: Certaines parties du contenu de ce projet (code, documentation, README) ont été générées par ChatGPT.
