set -e
cd "$(dirname "$0")/.."
../../.venv/bin/python ../../core/tts/tts.py tts/lines.json out/raw > out/tts.log 2>&1
HF_HUB_OFFLINE=1 ../../../.venv-cb/bin/python tts/cb.py > out/cb.log 2>&1
echo VOICE_DONE
