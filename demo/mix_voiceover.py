# Mix the voiceover onto the silent demo cut: cut at each caption change, hold the
# last frame so every line plays at 1.0x, then loudnorm to -16 LUFS.
import subprocess, glob
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
os.makedirs("vo", exist_ok=True); os.chdir("vo")
src="../citescout-demo.mp4"  # silent cut produced by record.sh
cuts=[0,2.9,6.65,8.9,14.65,18.9,23.65,30.9,36.9,40.4,43.4,53.1]
wav={}
for i in range(1,12):  # normalise TTS WAVs (24 kHz, no channel layout) to 48 kHz mono
    subprocess.run(['ffmpeg','-y','-v','error','-i',f'../../vo/cs-vo-line{i}.wav','-ac','1','-ar','48000','-c:a','pcm_s16le',f'n{i}.wav'],check=True)
    wav[i]=f'n{i}.wav'
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
lead=0.35; tail=0.7
starts=[];t=0;parts=[]
for i in range(11):
    a,b=cuts[i],cuts[i+1]
    if i==9: a=40.65
    seg=b-a; need=lead+dur(wav[i+1])+(1.6 if i==10 else tail)
    pad=max(0,need-seg); out=f"b{i+1}.mp4"
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(a),'-to',str(b),'-i',src,'-vf',f'tpad=stop_mode=clone:stop_duration={pad:.2f},fps=25','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out],check=True)
    starts.append(t+lead); t+=dur(out); parts.append(out)
open('l.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','l.txt','-c','copy','video.mp4'],check=True)
inputs=[];fl=[]
for i in range(11):
    inputs+=['-i',wav[i+1]]; ms=int(starts[i]*1000); fl.append(f"[{i+1}:a]adelay={ms}|{ms}[a{i}]")
fl.append(''.join(f"[a{i}]" for i in range(11))+"amix=inputs=11:normalize=0,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]")
subprocess.run(['ffmpeg','-y','-v','error','-i','video.mp4']+inputs+['-filter_complex',';'.join(fl),'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','citescout-demo-vo.mp4'],check=True)
print('starts',[round(s,2) for s in starts],'total',round(t,2))
