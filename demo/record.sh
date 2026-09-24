#!/usr/bin/env bash
# Record the citescout demo: segment 1 = web UI (Chrome), segment 2 = terminal (CLI).
# Usage: demo/record.sh   (runs on DISPLAY :99, writes demo/out/)
set -u
export DISPLAY=:99
cd "$(dirname "$0")/.."
source ~/venv/bin/activate
set -a; . ~/.citescout.env; set +a
mkdir -p demo/out
xset s off 2>/dev/null

rec_start() { ffmpeg -y -f x11grab -framerate 25 -video_size 1280x800 -i :99 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$1" -loglevel error & echo $!; }
rec_stop() { kill -INT "$1"; for i in $(seq 1 30); do kill -0 "$1" 2>/dev/null || return 0; sleep 0.3; done; kill -9 "$1" 2>/dev/null; }

pkill -f 'google-chrome' 2>/dev/null; pkill -f xfce4-terminal 2>/dev/null; sleep 1

echo "== segment 1: web UI"
FFPID=$(rec_start demo/out/seg1.mp4)
sleep 1.5
python demo/record_web.py "Is the Python requests library still maintained, or should I switch to httpx?"
rec_stop "$FFPID"
pkill -f 'google-chrome' 2>/dev/null; sleep 1

echo "== segment 2: terminal"
xfce4-terminal --maximize --hide-menubar --hide-borders --hide-scrollbar --font='Monospace 15' -x bash "$PWD/demo/terminal.sh" &
sleep 2
FFPID=$(rec_start demo/out/seg2.mp4)
# wait until terminal.sh is done (pytest finished): poll for the terminal process content end marker
while pgrep -f 'demo/terminal.sh' > /dev/null; do sleep 1; done
sleep 2
rec_stop "$FFPID"
pkill -f xfce4-terminal 2>/dev/null; sleep 1

echo "== concat"
printf "file '%s'\nfile '%s'\n" "$PWD/demo/out/seg1.mp4" "$PWD/demo/out/seg2.mp4" > demo/out/list.txt
ffmpeg -y -f concat -safe 0 -i demo/out/list.txt -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p demo/out/citescout-demo.mp4 -loglevel error
ffprobe -v error -show_entries format=duration -of csv=p=0 demo/out/citescout-demo.mp4
echo "done: demo/out/citescout-demo.mp4"
