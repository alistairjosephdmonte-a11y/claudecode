#!/bin/bash
# Final pass: audio gain + limiter, and trim the container to exactly 15.000 s (removes AAC padding).
set -e
in=out/the-seat-is-taken.mp4; out=out/the-seat-is-taken-final.mp4
ffmpeg -loglevel error -y -i "$in" -c:v copy -af "volume=${1:-4}dB,alimiter=limit=0.89:level=false,atrim=0:15" -c:a aac -b:a 256k -t 15 -movflags +faststart "$out"
ffmpeg -hide_banner -i "$out" 2>&1 | grep -E "Duration"
