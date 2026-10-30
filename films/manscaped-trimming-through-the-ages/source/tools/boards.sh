#!/bin/sh
# storyboard sheets: six frames per chapter (one per beat + the punchline hold) → sheets/board_NN.jpg
cd "$(dirname "$0")/../../.."
F=films/manscaped-trimming-through-the-ages; O=$F/out/board; mkdir -p $O
for n in ${@:-1 2 3 4 5 6 7 8 9 10}; do b=$(( (n - 1) * 30 ))
  rm -f $O/c${n}_*; k=0; for u in 3.5 9.5 16 22.5 27.5 29.9; do k=$((k + 1)); node core/render/still.mjs $F $(echo "$b + $u" | bc) --size 1440x1080 --prefix c${n}_${k}_ --out $O 2>&1 | grep -iE "error"; done
  ffmpeg -loglevel error -y -pattern_type glob -i "$O/c${n}_*.jpg" -vf "scale=640:480,tile=3x2:padding=8:color=0xF4EFE3" $F/sheets/board_$(printf %02d $n).jpg
done
