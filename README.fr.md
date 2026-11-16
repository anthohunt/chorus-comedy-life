[English](README.md) · **Français**

# Chorus Comedy Life

**La régie son d'un spectacle, dans une page web.** Chaque morceau part sur un clic avec ses propres fondus, l'ambiance du tableau tourne en boucle dessous, et tous les fichiers sont chargés avant le début du spectacle.

[![La vraie régie avec une liste de démonstration : l'ambiance du tableau tourne, l'ouverture démarre, un saut dans son fondu de sortie fait revenir l'ambiance (cliquer pour la vidéo complète)](docs/demo.gif)](https://drive.google.com/file/d/1MWjlYt6Ng0mRCqeQCAyLu0-0qvqBfsSd/view)

*La vraie régie avec une liste de démonstration et des sons synthétiques ; la vidéo est muette. [Vidéo complète (1:12)](https://drive.google.com/file/d/1MWjlYt6Ng0mRCqeQCAyLu0-0qvqBfsSd/view)*

## Ce qu'on fait avec

- **Tableaux.** Une liste numérotée par tableau : cliquer un morceau, puis Lecture.
- **Ambiance.** Une boucle par tableau, avec son volume. Sous un morceau, elle descend à 15 % ou s'arrête, selon le bouton Amb du morceau.
- **Fondus.** Fondu d'entrée et de sortie en secondes pour chaque morceau, en bleu et en jaune sur sa barre de progression. Un morceau peut s'arrêter à une seconde donnée.
- **Transport.** Lecture, pause, arrêt. Un clic sur la barre déplace dans le morceau ; le panneau de droite affiche le morceau en cours en grand.
- **Préchargé.** Tous les fichiers sont mis en cache à l'ouverture de la page ; un point vert marque chaque morceau prêt.
- **Mastering.** `outils/masteriser.sh` cuit coupes et fondus dans le fichier, à −14 LUFS, 256 kb/s, 44,1 kHz : ce qui joue en répétition est ce qui jouera le soir.

## Architecture

![Architecture : les morceaux sont coupés et normalisés par masteriser.sh, puis déposés dans sons/ ; server.py lit cues.json et sert la page, la liste et tous les MP3 à la régie dans le navigateur, qui joue un morceau par clic sur la sono de la salle ; une instance de test fait tourner le même code avec un bandeau rouge](docs/architecture.svg)

## Déploiement

- **Usage.** Répétitions d'une comédie musicale, à partir de mai 2026 : trois tableaux, chacun avec son ambiance.
- **Hébergement.** Service Python derrière HTTPS sur un serveur personnel, avec une instance de test à bandeau rouge où chaque changement était vérifié avant la mise en ligne. Retiré le 5 novembre 2026 et archivé.
- **Ce dépôt.** La même régie avec une liste d'exemple (`cues.json`) et quatre sons synthétiques (`sons/`). Python 3.8 ou plus, aucune dépendance ; ffmpeg seulement pour le mastering.
- **Ne marche pas encore.** Réordonner les morceaux par la poignée ☰ ; les curseurs de volume du pied de page ne couvrent que les deux premiers tableaux.

## Lancer

```
python3 server.py                               # http://127.0.0.1:8080
python3 server.py --port 8081 --banner "TEST"   # instance de test à bandeau rouge
outils/masteriser.sh morceau.wav sons/morceau.mp3 --debut 5 --fin 140 --fondu-sortie 6
```

Décrire ses tableaux dans `cues.json` (`name`, `ambiance`, `ambVolume`, `songs` ; par morceau `fadeIn`, `fadeOut`, `ambUnder`, `endAt`). Les morceaux du commerce sont des œuvres protégées : les garder hors du dépôt.

---

**Anthony Hunt** · [ingevision.cloud](https://ingevision.cloud/?p=chorus-comedy-life) · [LinkedIn](https://www.linkedin.com/in/anthony-hunt-3948a9196) · [GitHub](https://github.com/anthohunt)

Code : Apache 2.0. Textes et sons d'exemple : CC BY 4.0.
