import sys
import os
sys.path.append("../src")

import subprocess
from storage.firebase_storage import firebase_storage_instance

def optimize_video_for_reels( input_file ):

    output_file = os.path.join('src','output_downloads', 'reeloptimized-' + os.path.basename(input_file))
    scale_filter = "scale=-2:1080"  # adjust the height to 1080 pixels and maintain the aspect ratio

    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-c:v", "libx264",
        "-brand", "mp42",
        "-pix_fmt", "yuv420p",
        "-profile:v", "main",
        "-level", "3.1",
        "-preset", "medium",
        "-tune", "fastdecode",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ac", "2",
        "-ar", "48000",
        "-maxrate", "25M",
        "-bufsize", "30M",
        "-vf", scale_filter,
        "-r", "60",
        "-f", "mp4",
        "-y", output_file
    ]

    subprocess.call(cmd)
    return output_file

def convert_local_video_to_mp3(input_file):
    output_file = input_file.replace('.mp4', '.mp3')

    # Run FFMPEG command to convert mp4 to mp3
    subprocess.run([
        "ffmpeg", "-y", 
        "-i", input_file, 
        "-vn", 
        "-ar", "44100", 
        "-ac", "2", 
        "-b:a", "192k", 
        output_file
    ])
    print('Conversion to mp3 successful')
    return output_file
    
# def get_downloaded_video_local_path( remote_video_url ):
#     try:
#         upload_file_path = download_video(remote_video_url)
#         # firebase_storage_instance.upload_file_to_storage(
#         #     "ai_content_video/" + upload_file_path,
#         #     upload_file_path
#         # )
#         return upload_file_path
#     except Exception as e:
#         print(f'Error downloading video: {e}')
#         return    
    
def local_video_to_mp3( local_mp4_path ):
    mp3_path = local_mp4_path
    improved_mp3_path = mp3_path.replace('.mp4', '.mp3')
    # Set the FFmpeg command and arguments
    command = ["ffmpeg", "-y", "-i", local_mp4_path, "-vn", "-acodec", "libmp3lame", "-f", "mp3", improved_mp3_path]
    subprocess.call(command) # Run the command using subprocess
    print("Conversion complete!")
    return improved_mp3_path
