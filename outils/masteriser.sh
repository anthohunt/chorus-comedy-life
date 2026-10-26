#!/bin/bash
# masteriser.sh : prépare un morceau pour la régie. Toutes les coupes, tous les fondus sont cuits dans le fichier :
# ce que l'opérateur entend en répétition est exactement ce qui jouera le soir du spectacle.
# Cible unique : -14 LUFS, 256 kb/s, 44,1 kHz, MP3.
#
#   masteriser.sh ENTREE SORTIE.mp3 [--debut S] [--fin S] [--fondu-entree S] [--fondu-sortie S]
#   masteriser.sh --enchainer A B SORTIE.mp3 [--duree-fondu S]      # fondu enchaîné entre deux fichiers
set -euo pipefail
CIBLE='loudnorm=I=-14:TP=-1.5:LRA=11'
FIN_ARGS=(-ar 44100 -b:a 256k)
if [ "${1:-}" = "--enchainer" ]; then
  A=$2; B=$3; OUT=$4; D=2
  [ "${5:-}" = "--duree-fondu" ] && D=${6:-2}
  ffmpeg -loglevel error -y -i "$A" -i "$B" -filter_complex "[0][1]acrossfade=d=$D,$CIBLE" "${FIN_ARGS[@]}" "$OUT"
  echo "ok : $OUT"; exit 0
fi
[ $# -ge 2 ] || { sed -n 2,9p "$0" | sed 's/^# \{0,1\}//'; exit 1; }
IN=$1; OUT=$2; shift 2
DEBUT=""; FIN=""; FIN_IN=0; FIN_OUT=0
while [ $# -gt 0 ]; do
  case $1 in
    --debut) DEBUT=$2; shift 2 ;;
    --fin) FIN=$2; shift 2 ;;
    --fondu-entree) FIN_IN=$2; shift 2 ;;
    --fondu-sortie) FIN_OUT=$2; shift 2 ;;
    *) echo "option inconnue : $1" >&2; exit 1 ;;
  esac
done
F=""
if [ -n "$DEBUT$FIN" ]; then F="atrim=${DEBUT:+start=$DEBUT}${DEBUT:+${FIN:+:}}${FIN:+end=$FIN},asetpts=PTS-STARTPTS,"; fi
[ "$FIN_IN" != 0 ] && F="${F}afade=t=in:st=0:d=$FIN_IN,"
if [ "$FIN_OUT" != 0 ]; then
  DUREE=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
  FIN_EFF=${FIN:-$DUREE}; DEB_EFF=${DEBUT:-0}
  ST=$(python3 -c "print(max(0, $FIN_EFF - $DEB_EFF - $FIN_OUT))")
  F="${F}afade=t=out:st=$ST:d=$FIN_OUT,"
fi
ffmpeg -loglevel error -y -i "$IN" -af "${F}${CIBLE}" "${FIN_ARGS[@]}" "$OUT"
echo "ok : $OUT"
