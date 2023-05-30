import sys
import os
import meta_graph_api.meta_tokens as meta_tokens
from domain.endpoint_definitions import make_api_call
import media.image_creator as image_creator
import appsecrets as appsecrets
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import domain.url_shortener as url_shortener
import storage.dropbox_storage as dropbox_storage
import ai.gpt as gpt
import json
import requests

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

def chunk_video_upload( post_json_object ):
    local_video_path = dropbox_storage.download_file_to_local_path(post_json_object['url'])
    file_size = os.path.getsize(local_video_path)
    page_id=post_json_object['page_id']
    print(f'⚙️ Processing file size: {file_size}')

    # Step 1: Upload the video
    video_response = requests.post(
        f'https://graph-video.facebook.com/{page_id}/videos',
        params={ 
            'access_token': post_json_object['access_token'],
            'upload_phase': 'start',
            'file_size': file_size  # Replace with the actual file size
        }
    )

    # Step 2: Parse the video ID and upload session ID from the response
    video_id = video_response.json()['video_id']
    upload_session_id = video_response.json()['upload_session_id']

    # Step 3: Upload the video in chunks
    with open(local_video_path, 'rb') as file:
        chunk_size = 4 * 1024 * 1024  # 4MB
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            upload_response = requests.post(
                f'https://graph-video.facebook.com/{page_id}/videos',
                params={
                    'access_token': post_json_object['access_token'],
                    'upload_phase': 'transfer',
                    'start_offset': file.tell() - len(chunk),
                    'upload_session_id': upload_session_id
                },
                files={
                    'video_file_chunk': chunk
                }
            )
            upload_json = json.loads( upload_response.content ) # response data from the api
            pretty_upload_json = json.dumps( upload_json, indent = 4 ) # pretty print for cli

            print(pretty_upload_json)

    # Step 4: Finish the video upload
    finish_response = requests.post(
        f'https://graph-video.facebook.com/{page_id}/videos',
        params={
            'access_token': post_json_object['access_token'],
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            'description': post_json_object['description']
        }
    )
    return finish_response, video_id

def post_to_page( firebase_object ):
    params = meta_tokens.fetch_fb_page_access_token()
    params['access_token'] = params['page_access_token']
    params['page_id'] = appsecrets.FACEBOOK_GRAPH_API_PAGE_ID
    return post_content(params, firebase_object)

def post_content( params, firebase_object ):

    if (firebase_object['media_type'] == 'IMAGE'):
        url = params['endpoint_base'] + params['page_id'] + '/photos'

        params['message'] = firebase_object['message']
        params['url'] = firebase_object['url']

        response = make_api_call( url=url, req_json=params, type='POST')
        return response
    
    elif (firebase_object['media_type'] == 'VIDEO'):  
        
        params['url'] = firebase_object['url']
        params['description'] = firebase_object['message']

        response, video_id = chunk_video_upload(params)
        return response

def post_scheduled_fb_post( scheduled_datetime_str ):
    firebase_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.FACEBOOK, 
        scheduled_datetime_str
    )
    try:
        post_json_object = json.loads(firebase_json)
        print(f'📦 FB {post_json_object}')
    except:
        print(f'🔥FB error {firebase_json}')
        return ''
        
    page_result = post_to_page(post_json_object)
    return page_result

def post_to_facebook(is_testmode=False):
    '''
    Method called from main class that creates our endpoint request and makes the API call.
    Also, prints status of uploading the payload.

    @returns: nothing
    '''
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.FACEBOOK,
        post_scheduled_fb_post,
        is_test = is_testmode
    )

def schedule_fb_post( caption, image_query ):
    if (image_query is None or image_query == '' or caption is None or caption == ''):
        print('🔥 Error scheduling for FB')
        return ''
    
    image_url = image_creator.get_unsplash_image_url(image_query, PostingPlatform.FACEBOOK)
    payload = {
        'media_type': 'IMAGE',
        'url': image_url,
        'message': caption, 
        'published' : True
    }
    result = firebase_storage_instance.upload_scheduled_post(
        PostingPlatform.FACEBOOK, 
        payload
    )
    print('📦 FB upload scheduled post result' + str(result))
    return result
    
# def post_blog_promo( blog_title, ref_url ):
#     short_url = url_shortener.shorten_tracking_url(
#         url_destination=ref_url,
#         slashtag='',
#         platform=PostingPlatform.FACEBOOK,
#         campaign_medium='blog-reference',
#         campaign_name=blog_title
#     )
#     message=gpt.link_prompt_to_string(
#         prompt_source_file=os.path.join("src", "input_prompts", "facebook_blog_ref.txt"),
#         feedin_title=blog_title,
#         feedin_link=short_url
#     )
#     payload = {
#         'link': short_url,
#         'message': message, 
#         'published' : True
#     }
#     make_fb_feed_call_with_token(payload)  

def schedule_fb_video_post( caption, db_remote_path ):    
    if (db_remote_path is None or db_remote_path == '' or caption is None or caption == ''):
        print('🔥 Error scheduling for FB')
        return ''
    
    payload = {
        'media_type': 'VIDEO',
        'url': db_remote_path,
        'message': caption, 
        'published' : True
    }
    result = firebase_storage_instance.upload_scheduled_post(
        PostingPlatform.FACEBOOK, 
        payload
    )
    print(f'⏰ FB scheduled!{result}')
