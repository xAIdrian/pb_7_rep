import sys
import os
import libs.tiktok_uploader 

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

# Publish the video
tiktok_uploader.uploadVideo(session_id, file, title, tags)
# Schedule the video
# uploadVideo(session_id, file, title, tags, schedule_time, verbose=True)
