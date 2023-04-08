import sys
import os
sys.path.append("../src")
import libs.tiktok_uploader 

# Publish the video
tiktok_uploader.uploadVideo(session_id, file, title, tags)
# Schedule the video
# uploadVideo(session_id, file, title, tags, schedule_time, verbose=True)