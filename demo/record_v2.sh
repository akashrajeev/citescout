#!/usr/bin/env bash
# Record the round-2 citescout demo: web UI segment, then terminal segment.
# Usage: demo/record_v2.sh   (DISPLAY :98, citescout-web already running on :8000; writes demo/out/)
set -u
export DISPLAY=:98
cd "$(dirname "$0")/.."
source ~/.venv/bin/activate 2>/dev/null || source ~/venv/bin/activate
mkdir -p demo/out
rec_start() { ffmpeg -y -f x11grab -framerate 25 -video_size 1280x800 -i :98 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$1" -loglevel error </dev/null >/dev/null 2>&1 & echo $!; }
rec_stop() { kill -INT "$1"; for i in $(seq 1 30); do kill -0 "$1" 2>/dev/null || return 0; sleep 0.3; done; kill -9 "$1" 2>/dev/null; }
pkill -f 'google-chrome' 2>/dev/null; pkill -f xfce4-terminal 2>/dev/null; sleep 1
T0=$(date +%s.%N); FFPID=$(rec_start demo/out/v2-seg1.mp4)
python demo/record_web_v2.py "Is the Python requests library still maintained, or should I switch to httpx?" "$T0"
rec_stop "$FFPID"; pkill -f 'google-chrome' 2>/dev/null; sleep 1
xfce4-terminal --maximize --hide-menubar --hide-borders --hide-scrollbar --font='Monospace 15' -x bash "$PWD/demo/terminal_v2.sh" &
sleep 2
FFPID=$(rec_start demo/out/v2-seg2.mp4)
while pgrep -f 'demo/terminal_v2.sh' > /dev/null; do sleep 1; done
sleep 1; rec_stop "$FFPID"; pkill -f xfce4-terminal 2>/dev/null
for s in 1 2; do ffprobe -v error -show_entries format=duration -of csv=p=0 demo/out/v2-seg$s.mp4; done
