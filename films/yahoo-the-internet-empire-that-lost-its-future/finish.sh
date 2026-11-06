set -e
cd /home/user/yh/out
until [ $(grep -l CHUNK_DONE k4_*.log 2>/dev/null | wc -l) -eq 4 ]; do sleep 30; done
for i in 0 1 2 3; do ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets,width -of csv=p=0 k4_$i.mp4; done
printf "file 'k4_0.mp4'\nfile 'k4_1.mp4'\nfile 'k4_2.mp4'\nfile 'k4_3.mp4'\n" > k4.txt
J=$(ffmpeg -hide_banner -nostats -i ../audio/mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g(){ echo "$J" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
LN="loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000"
C="-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv"
F=/home/user/yh/deliver; mkdir -p $F/segments $F/audio
ffmpeg -y -loglevel error -f concat -safe 0 -i k4.txt -i ../audio/mix.wav -filter_complex "[0:v]format=yuv420p[v];[1:a]$LN[a]" -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -r 24 $C -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -shortest $F/BRAND_CORONER_CASE008_YAHOO_FINAL_4K.mp4
rm -f k4_*.mp4
ffmpeg -y -loglevel error -i $F/BRAND_CORONER_CASE008_YAHOO_FINAL_4K.mp4 -vf "scale=1920:1080:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 19 $C -c:a copy -movflags +faststart $F/BRAND_CORONER_CASE008_YAHOO_1080p_YouTube.mp4
# audio deliverables: narration WAV, music stem, effects stem (48 kHz)
for s in narration music foley; do ffmpeg -y -loglevel error -i ../audio/stems/$s.wav -ar 48000 -c:a pcm_s16le $F/audio/$s.wav; done
# 16 scene-level segments (cut from the 1080p master at scene boundaries)
python3 - <<'PY'
import json, subprocess
t = json.load(open('/home/user/yh/vo/timeline.json'))
for s in t['scenes']:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(s['base']), '-t', str(s['dur']), '-i', '/home/user/yh/deliver/BRAND_CORONER_CASE008_YAHOO_1080p_YouTube.mp4',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', f"/home/user/yh/deliver/segments/S{s['i']:02d}.mp4"], check=True)
PY
ls -la $F $F/segments $F/audio
for f in $F/BRAND*.mp4; do ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets,width,height -show_entries format=duration -of csv=p=0 $f; done
ffmpeg -hide_banner -nostats -i $F/BRAND_CORONER_CASE008_YAHOO_FINAL_4K.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | head -1
echo FINISHED
