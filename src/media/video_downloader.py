import youtube_dl
import subprocess
from storage.firebase_storage import firebase_storage_instance

"""Save a YouTube video URL to mp3.

    Args:
       # url (str): A YouTube video URL.

    Returns:
        #str: The filename of the mp3 file.
"""        
def save_to_mp3(url):
    options = {
        'outtmpl': 'src/output_downloads/%(title)s-%(id)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'nocheckcertificate': True,
        'retries': 20
     }

    with youtube_dl.YoutubeDL(options) as downloader:
        print('Preparing download...')
        downloader.download(["" + url + ""])
        return downloader.prepare_filename(downloader.extract_info(url, download=False)).replace(".m4a", ".mp3").replace(".webm", ".mp3").replace(".mp4", ".mp3")

def download_video( url ):
    options = options = {
        'outtmpl': 'src/output_downloads/%(title)s-%(id)s.%(ext)s',
        'format': 'bestvideo/best',
        'nocheckcertificate': True
     }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(["" + url + ""]) 
        
        extracted_info = ydl.extract_info(url, download=False)
        file_path = ydl.prepare_filename(extracted_info) 

        return file_path
    
def get_downloaded_video_local_path( remote_video_url ):
    try:
        upload_file_path = download_video(remote_video_url)
        # firebase_storage_instance.upload_file_to_storage(
        #     "ai_content_video/" + upload_file_path,
        #     upload_file_path
        # )
        return upload_file_path
    except Exception as e:
        print(f'Error downloading video: {e}')
        return    
    
def local_video_to_mp3( local_mp4_path ):
    mp3_path = local_mp4_path.replace('.mp4', '.mp3')
    # Set the FFmpeg command and arguments
    command = ["ffmpeg", "-i", local_mp4_path, "-vn", "-acodec", "libmp3lame", "-f", "mp3", mp3_path]
    subprocess.call(command) # Run the command using subprocess
    print("Conversion complete!")
    return mp3_path
