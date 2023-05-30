import sys
import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import ai.gpt as gpt3
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import storage.dropbox_storage as dropbox_storage
import pickle
import json
import ai.gpt as gpt
import media.video_editor as video_editor
from ai.gpt_write_story import create_story_and_scenes
import utility.scheduler as scheduler
import media.video_converter as video_converter
import utility.time_utils as time_utils
import utility.text_utils as text_utils

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

# Build the YouTube API client
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

CLIENT_SECRET_FILE = "google_youtube_client.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtubepartner'
]

# Note that this works only for shorts ATM
def complete_scheduling_and_posting_of_video ( remote_video_path ): 
    print('Begining YT scheduling...')
    creds = get_youtube_credentials()
    if creds == '': return ''

    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, 
        API_VERSION, 
        credentials = creds
    )

    summary_file = os.path.join('src', 'outputs', 'summary_output.txt')

    title = gpt3.prompt_to_string_from_file(
        os.path.join('src', 'input_prompts', 'youtube_title.txt'),
        feedin_source_file=summary_file
    )
    title = text_utils.format_yt_title(title)

    description = gpt3.prompt_to_string_from_file(
        prompt_source_file=os.path.join('src', 'input_prompts', 'youtube_description.txt'),
        feedin_source_file=summary_file
    )
    description = text_utils.format_yt_description(description)

    upload_file_path = dropbox_storage.download_file_to_local_path(remote_video_path)
    posting_time = scheduler.get_best_posting_time(PostingPlatform.YOUTUBE)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "17"
            },
            "status": {
                "privacyStatus": "private",
                "embeddable": True,
                "license": "youtube",
                "publicStatsViewable": True,
                "publishAt": posting_time
            }
        },
        media_body=MediaFileUpload(upload_file_path)
    )
    try:
        response = request.execute()
        print(f'⏰ YT posting scheduled!\n{response}')   
        firebase_storage_instance.upload_scheduled_post(
            PostingPlatform.YOUTUBE,
            payload = {
                "title": title,
                "description": description,
                "video_url": upload_file_path
            }
        ) 
    except Exception as e:    
        print(f'Youtube error {e}')
        response = e
        
    return response

def scheduled_youtube_video ( remote_video_url ):  
    if (remote_video_url is None or remote_video_url == ''):
        print('🔥 Error scheduling YT')
        return ''
    
    summary_file = os.path.join('src', 'outputs', 'summary_output.txt')
    title = gpt3.prompt_to_string_from_file(
        os.path.join('src', 'input_prompts', 'youtube_title.txt'),
        feedin_source_file=summary_file
    )
    title = title.replace('"', '')
    description = gpt3.prompt_to_string_from_file(
        prompt_source_file=os.path.join('src', 'input_prompts', 'youtube_description.txt'),
        feedin_source_file=summary_file
    )
    yt_tags = gpt3.prompt_to_string_from_file(
        prompt_source_file=os.path.join('src', 'input_prompts', 'youtube_tags.txt'),
        feedin_source_file=summary_file
    )
    tags_array = yt_tags.replace(',', '').replace('#', '').split(' ')

    payload = dict()
    payload['title'] = title
    payload['description'] = description
    payload['remote_video_url'] = remote_video_url
    payload['tags']: tags_array

    result = firebase_storage_instance.upload_scheduled_post(
        PostingPlatform.YOUTUBE,
        payload
    )
    return result

def get_youtube_credentials():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get credentials and create an API client
    # Get the path to the parent directory
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(parent_dir, CLIENT_SECRET_FILE)
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(file_path, SCOPES)

    # get cached values
    try:
        token_file = os.path.join('src', 'yt_access_token.pickle')
        with open(token_file, "rb") as input_file:
            credentials = pickle.load(input_file)

        if (credentials == ''):
            credentials = flow.run_local_server()
            
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)  
    except:
        print('🔥 YT error getting cached credentials')
        # this is bad and needs to be updated
        # credentials = flow.run_local_server()
        
        # with open(token_file, 'wb') as token:
        #     pickle.dump(credentials, token)

    print(f'✅ YT authentication complete and approved!')
    return credentials

def post_previously_scheduled_youtube_video():
    earliest_scheduled_datetime_str = firebase_storage_instance.get_earliest_scheduled_datetime(PostingPlatform.YOUTUBE)
    if (earliest_scheduled_datetime_str == ''): 
        return 'no posts scheduled'
    
    ready_to_post = time_utils.is_current_posting_time_within_window(earliest_scheduled_datetime_str)
    if (ready_to_post):  
        print(f'✅ YT earliest_scheduled_datetime_str: {earliest_scheduled_datetime_str} coincides with already scheduled time')
        response = firebase_storage_instance.delete_post(
            PostingPlatform.YOUTUBE, 
            earliest_scheduled_datetime_str
        )
        return response

def post_youtube_video():    
    response = post_previously_scheduled_youtube_video()
    print(f'📦 YT response {response}') 

def process_initial_video_download_transcript(db_remote_path, should_summarize=True):
    filename = video_converter.local_video_to_mp3(db_remote_path)
    transcriptname = gpt.mp3_to_transcript(filename)
    if (should_summarize): gpt.transcript_to_summary(transcriptname, filename) 

def schedule_video_story(image_query):
    gpt.generate_video_with_prompt(
        prompt_source=os.path.join("src", "input_prompts", "story.txt"), 
        video_meta_data=image_query,
        post_num=1,
        upload_func=create_story_and_scenes
    )
    video_remote_url = video_editor.edit_movie_for_remote_url(image_query)
    if (video_remote_url != ''):
        result = complete_scheduling_and_posting_of_video(video_remote_url)
        print(f'⏰ YT scheduled! \n{result}')
    else:
        print('🔥 YT error getting remote video url')    

def get_recent_videos():
    # Set up the YouTube API client
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=get_youtube_credentials())

    # Retrieve the most recent videos uploaded to your channel
    request = youtube.search().list(
        part="snippet",
        channelId='UCI4DX-IyQ8KAGhPWE0Qr7Vg',
        order="date",
        type="video",
        maxResults=10
    )
    response = request.execute()

    # Print the title and video ID of each video in the response
    for item in response["items"]:
        print(f'📦 Title: {item["snippet"]["title"]} && Video ID: {item["id"]["videoId"]}')
