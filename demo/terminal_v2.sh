#!/usr/bin/env bash
# Terminal half of the round-2 demo: credits left, eval scores (0 credits), tests.
cd "$(dirname "$0")/.."
source ~/.venv/bin/activate 2>/dev/null || source ~/venv/bin/activate 2>/dev/null || true
set -a; [ -f ~/.citescout.env ] && . ~/.citescout.env; set +a
p() { printf '\033[1;32makash@dev\033[0m:\033[1;34m~/citescout\033[0m$ '; for ((i=0;i<${#1};i++)); do printf '%s' "${1:$i:1}"; sleep 0.045; done; echo; sleep 0.6; }
clear
p "citescout budget"
citescout budget
sleep 2.5
p "citescout eval --rescore"
citescout eval --rescore 2>&1 | sed -n '/Totals/,/(100%)/p'
sleep 7
p "pytest -q"
pytest -q
sleep 5
