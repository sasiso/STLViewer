import os
import subprocess

def open_folder_in_explorer(folder_path):
    try:
        subprocess.Popen(['explorer', folder_path], shell=True)
    except Exception as e:
        print(f"Error: {e}")


def encode(file_name=None):

    import subprocess

    ffmpeg_path = "ffmpeg.exe"
    input_pattern = "frame_%03d.png"
    output_file = file_name if file_name else "output.mp4"
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
        
        open_folder_in_explorer(working_directory)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
