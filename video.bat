@echo off
cd /d temp_images

set FFmpegPath=ffmpeg.exe
set InputPattern=frame_%%03d.png
set OutputFile=output.mp4

%FFmpegPath% -framerate 24 -start_number 1 -i '%InputPattern%' -c:v libx264 -pix_fmt yuv420p %OutputFile%

echo Done!
pause
