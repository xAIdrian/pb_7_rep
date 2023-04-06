import sys
import os
sys.path.append("../src")

import dropbox
from dropbox.exceptions import AuthError
from storage.firebase_storage import firebase_storage_instance
import appsecrets
import requests

DB_FOLDER_READY = "/ShortVideoReady"
DB_FOLDER_SCHEDULED = '/ShortVideoScheduled'
DB_FOLDER_POSTED = '/ShortVideoPosted'

def initialize_dropbox():
        """Create a connection to Dropbox."""
        token = firebase_storage_instance.get_complete_access_token(firebase_storage_instance.DROPBOX_ACCESS_TOKEN)
        if (token is None or token == ''):  
            # get code here first : https://www.dropbox.com/oauth2/authorize?client_id=9vlc2zeelddxzek&token_access_type=offline&response_type=code 
            # Get the refresh token
            url = 'https://api.dropboxapi.com/oauth2/token'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'code': appsecrets.DROPBOX_AUTH_CODE,
                'grant_type': 'authorization_code'
            }
            auth = (appsecrets.DROPBOX_APP_ID, appsecrets.DROPBOX_APP_SECRET)
            response = requests.post(url, headers=headers, data=data, auth=auth)
            response_json = response.json()
            REFRESH_TOKEN = response_json['refresh_token']

            firebase_storage_instance.put_complete_access_token(
                firebase_storage_instance.DROPBOX_ACCESS_TOKEN,
                REFRESH_TOKEN
            )
            token = REFRESH_TOKEN
        # Use the refresh token to get the Dropbox object
        dbx = dropbox.Dropbox(
            app_key=appsecrets.DROPBOX_APP_ID,
            app_secret=appsecrets.DROPBOX_APP_SECRET,
            oauth2_refresh_token=token
        )
        print('Dropbox Initialized Successfully')
        return dbx        

dbx = initialize_dropbox() 

def get_file_name_from_path( file_path ):
    # Split the path into a list of directories and the file name
    directories = file_path.split('/')
    file_name = None

    # Traverse the directories list backwards to find the last .mp4 file
    for directory in reversed(directories):
        if directory.endswith('.mp4'):
            file_name = directory
            break

    # Check if a .mp4 file was found
    if file_name is None:
        print("There is no .mp4 file in the path.")
        return ''
    else:
        print("The last .mp4 file name is:", file_name)
        return file_name
    
def download_file_to_local_path( remote_file_path):

    local_download_path = os.path.join('src', 'output_downloads', get_file_name_from_path(remote_file_path))
    # Check if this is the earliest uploaded video file
    
    if (remote_file_path is None):
        print("No files found") 
        return ''
    elif (os.path.isfile(local_download_path)):
        print("File already downloaded")        
        return local_download_path
    else:
        # Download the earliest uploaded video file
        print('Downloading from dropbox...')
        with open(local_download_path, "wb") as f:
            metadata, res = dbx.files_download(path=remote_file_path)
            f.write(res.content)
        print(f"Earliest uploaded video file '{remote_file_path}' downloaded to '{local_download_path}'")
        return local_download_path

def get_streaming_download_url( file_path ):
    settings = dropbox.sharing.SharedLinkSettings(
        requested_visibility=dropbox.sharing.RequestedVisibility.public
    )
    link = dbx.sharing_create_shared_link_with_settings(file_path, settings=settings)
    url = link.url.replace('?dl=0', '').replace('www.dropbox', 'dl.dropboxusercontent')
    return url

def get_earliest_ready_short_video():
    # Get a list of all the files in the folder
    try:
        result = dbx.files_list_folder(DB_FOLDER_READY)
    except AuthError as e:
        print(e)
        initialize_dropbox()    

    # Initialize variables to track the earliest uploaded video file
    earliest_uploaded = None
    earliest_entry = None

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith('.mp4'):
            uploaded = entry.client_modified.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            if earliest_uploaded is None or uploaded < earliest_uploaded:
                print(f"Earliest updated: {entry.name}, uploaded @ {uploaded}")
                earliest_entry = entry
                earliest_uploaded = uploaded

    return earliest_entry

def upload_file( local_file_path, dropbox_file_path ):
    """Upload a file from the local machine to a path in the Dropbox app directory.

        Args:
            local_path (str): The path to the local file.
            local_file (str): The name of the local file.
            dropbox_file_path (str): The path to the file in the Dropbox app directory.

        Example:
            source_to_content(filename, transcriptname, 'prompts_input/blog.txt', "blog")

        Returns:
            meta: The Dropbox file metadata.
    """
    try:
        with open(local_file_path, "rb") as f:
            meta = dbx.files_upload(
                f.read(), 
                dropbox_file_path, 
                mode=dropbox.files.WriteMode("overwrite")
            )
            print("Upload success to DBX")
            return meta
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))          

def upload_file_for_sharing_url( local_file_path, dropbox_file_path ):
    upload_file(local_file_path, dropbox_file_path)
    return get_streaming_download_url(dropbox_file_path)

def move_file(source_path, destination_path):
    try:
        dbx.files_move_v2(source_path, destination_path)
        print(f'Moved {source_path} to {destination_path} successfully!')
    except AuthError as e:
        print(f'Error authenticating: {e}')
    except Exception as e:
        print(f'Error moving file: {e}')