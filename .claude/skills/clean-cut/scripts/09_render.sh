#!/bin/zsh
# Step 9 - check, render and make a phone copy.   09_render.sh <project_dir> "<out_dir>" "<Title>" <fps, e.g. 24000/1001>
# Render at the SOURCE frame rate (the same --fps given to 02_cut.py), so no frame is dropped or doubled.
set -e; P=$1; OUT=$2; TITLE=$3; FPS=${4:-30}; cd "$P"
npx hyperframes lint 2>&1 | tail -5
F="$OUT/$TITLE - Clean Cut 9x16.mp4"
npx hyperframes render -o "$F" --fps "$FPS" --quality looks 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E "rendered in|MB ·|rror" | tail -3
# phone copy around 23 MB, small enough to send from the chat
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F"); BR=$(python3 -c "print(int(min(2900, 23*8000/$D - 160)))")
PH="$OUT/$TITLE - Clean Cut (phone).mp4"
ffmpeg -v error -y -i "$F" -c:v libx264 -preset slow -b:v ${BR}k -maxrate $((BR*5/4))k -bufsize 6000k -c:a aac -b:a 160k -movflags +faststart "$PH"
echo "master: $F"; echo "phone:  $PH"
