# Mix the v2 voiceover onto the silent round-2 cut (record_v2.sh output).
# Cut at each beat logged by record_web_v2.py, hold the last frame so every line plays
# at 1.0x, then loudnorm to -16 LUFS. Usage: python demo/mix_voiceover_v2.py <pytest_start_in_seg2>
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(here, "out"))
os.makedirs("vo2", exist_ok=True)


def run(*a):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *a], check=True)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


run("-i", "v2-seg1.mp4", "-i", "v2-seg2.mp4", "-filter_complex", "[0:v]fps=25[a];[1:v]fps=25[b];[a][b]concat=n=2:v=1[v]",
    "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "vo2/silent.mp4")
beats = [float(l.split("\t")[0]) for l in open("beats.txt") if l.split("\t")[1].strip() not in ("end", "export")]  # line 12 covers evidence + export
s1 = dur("v2-seg1.mp4")
cuts = [0.0] + beats[1:] + [s1, s1 + float(sys.argv[1]), dur("vo2/silent.mp4")]
n = len(cuts) - 1
lines = [f"../../vo/cs2-vo-line{i}.wav" for i in range(1, n + 1)]
os.chdir("vo2")
assert all(os.path.exists(l) for l in lines), f"need {n} lines"
wav = []
for i, l in enumerate(lines, 1):
    run("-i", l, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", f"n{i}.wav")
    wav.append(f"n{i}.wav")
lead, tail = 0.35, 0.6
t, starts, parts = 0.0, [], []
for i in range(n):
    a, b = cuts[i], cuts[i + 1]
    need = lead + dur(wav[i]) + (1.5 if i == n - 1 else tail)
    pad = max(0.0, need - (b - a))
    out = f"b{i + 1}.mp4"
    run("-ss", f"{a:.2f}", "-to", f"{b:.2f}", "-i", "silent.mp4", "-vf", f"tpad=stop_mode=clone:stop_duration={pad:.2f},fps=25",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out)
    starts.append(t + lead)
    t += dur(out)
    parts.append(out)
open("l.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
run("-f", "concat", "-safe", "0", "-i", "l.txt", "-c", "copy", "video.mp4")
inputs, fl = [], []
for i in range(n):
    inputs += ["-i", wav[i]]
    ms = int(starts[i] * 1000)
    fl.append(f"[{i + 1}:a]adelay={ms}|{ms}[a{i}]")
fl.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,pan=stereo|c0=c0|c1=c0,"
          "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]")
run("-i", "video.mp4", *inputs, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]", "-c:v", "copy",
    "-c:a", "aac", "-b:a", "160k", "-shortest", "citescout-demo-v2.mp4")
print("starts", [round(s, 2) for s in starts], "total", round(t, 2))
