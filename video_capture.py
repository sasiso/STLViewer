import os
def encode():

    import subprocess

    ffmpeg_path = "ffmpeg.exe"
    input_pattern = "frame_%03d.png"
    output_file = "output.mp4"
    working_directory = os.path.join(os.getcwd(), 'temp_images')
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')

    # Build the FFmpeg command
    ffmpeg_command = [
        ffmpeg_path,
        "-y",  # Add the -y option to force overwrite
        "-framerate", "24",
        "-start_number", "1",
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_file
    ]

    # Execute the FFmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True, cwd=working_directory)
        print("Conversion completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
