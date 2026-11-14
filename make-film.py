from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,imageio_ffmpeg
out=Path('dist')
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
shots=[('河港','人和书跨越边界','教会随人迁移', '港'),('讲堂','从圣经解释恩典与信心','课堂问题走向教会', '学'),('会场','1618–1619 · 多特会议','条文回应救恩争议', '议'),('讲台','公开传讲基督','以神的应许安慰信徒', '恩')]
cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-pixel_format','rgb24','-video_size','800x450','-framerate','12','-i','-','-c:v','libx264','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'dort-film.mp4')]
with subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL) as p:
 for i,(title,line,sub,icon) in enumerate(shots):
  im=Image.new('RGB',(800,450),('#174d50','#384269','#603c59','#2d5745')[i]);d=ImageDraw.Draw(im)
  d.rounded_rectangle((575,129,740,294),32,fill='#f3cd83');d.text((657,207),icon,font=font(83),fill='#173d3b',anchor='mm')
  d.text((55,54),f'多特历史导览   0{i+1} / 04',font=font(23),fill='#f3cd83')
  d.text((55,115),title,font=font(82),fill='white');d.text((58,246),line,font=font(34),fill='white');d.text((58,304),sub,font=font(27),fill='#f3cd83')
  if i==0: im.save(out/'dort-film.jpg',quality=86)
  for f in range(72):
   frame=im.copy();ImageDraw.Draw(frame).rectangle((55,385,55+int(690*(i*72+f+1)/288),392),fill='#f3cd83');p.stdin.write(frame.tobytes())
 p.stdin.close()
 if p.wait():raise SystemExit('video encoding failed')
