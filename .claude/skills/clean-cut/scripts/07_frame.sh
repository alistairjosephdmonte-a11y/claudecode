#!/bin/zsh
# Step 7 - frame the cut as a 9:16 vertical video (1080x1920, with the audio).
#   07_frame.sh "<CUT.mp4>" "<out 9x16.mp4>" [w h x y]
# Horizontal source: pass a 9:16 crop window in source pixels with the face centred
#   (3840x2160 -> 1215 2160 <x> 0 ; 1920x1080 -> 608 1080 <x> 0). Work x out from a still first.
# Vertical source: pass nothing, it is only scaled to 1080x1920. The aspect ratio of a vertical clip never changes.
set -e; C=$1; O=$2
if [ -n "$3" ]; then VF="crop=$3:$4:$5:$6,scale=1080:1920:flags=lanczos"; else VF="scale=1080:1920:flags=lanczos"; fi
ffmpeg -v error -y -i "$C" -vf "$VF" -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$O"
ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "$O"
