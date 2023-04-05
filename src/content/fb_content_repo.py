import sys
import os
sys.path.append("../src")

import meta_graph_api.meta_tokens as meta_tokens
from domain.endpoint_definitions import make_api_call
import media.image_creator as image_creator
import appsecrets as appsecrets
import media.video_downloader as video_downloader
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import domain.url_shortener as url_shortener
import content.ig_content_repo as ig_content_repo
import ai.gpt as gpt
import json
import requests

def make_fb_feed_call_with_token( post_json_object ):
    params = meta_tokens.fetch_fb_page_access_token()
    post_json_object['access_token'] = params['page_access_token']
    print(f'FACEBOOK {post_json_object}')

    url = params['endpoint_base'] + appsecrets.FACEBOOK_GRAPH_API_PAGE_ID + '/feed'
    result = make_api_call( url=url, req_json=post_json_object, type='POST')
    print(result['json_data_pretty'] )
    return result

def chunk_video_upload( post_json_object ):
    local_video_path = video_downloader.download_video(post_json_object['url'])
    file_size = os.path.getsize(local_video_path)
    print(f'processing file size: {file_size}')
    # Step 1: Upload the video
    video_response = requests.post(
        f'https://graph-video.facebook.com/{appsecrets.FACEBOOK_GRAPH_API_PAGE_ID}/videos',
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
                f'https://graph-video.facebook.com/{appsecrets.FACEBOOK_GRAPH_API_PAGE_ID}/videos',
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
        f'https://graph-video.facebook.com/{appsecrets.FACEBOOK_GRAPH_API_PAGE_ID}/videos',
        params={
            'access_token': post_json_object['access_token'],
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            # 'title': 'My video title',
            'description': post_json_object['description']
        }
    )
    return finish_response, video_id

def make_fb_call_with_token( post_json_object ):
    params = meta_tokens.fetch_fb_page_access_token()

    params['access_token'] = params['page_access_token']
    post_json_object['access_token'] = params['page_access_token']

    print(f'FACEBOOK {post_json_object}')

    if (post_json_object['media_type'] == 'IMAGE'):
        url = params['endpoint_base'] + appsecrets.FACEBOOK_GRAPH_API_PAGE_ID + '/photos'
        result = make_api_call( url=url, req_json=post_json_object, type='POST')
        print(result['json_data_pretty'] )
        return result
    
    elif (post_json_object['media_type'] == 'VIDEO'):    
        url = params['endpoint_base'] + appsecrets.FACEBOOK_GRAPH_API_PAGE_ID + '/videos'
        
        post_json_object['url'] = post_json_object['url']
        post_json_object['description'] = post_json_object['message']
        post_json_object['published'] = post_json_object['published']

        response, video_id = chunk_video_upload(post_json_object)
        return response

def post_scheduled_fb_post( scheduled_datetime_str ):
    post_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.FACEBOOK, 
        scheduled_datetime_str
    )
    try:
        post_json_object = json.loads(post_json)
    except:
        print(F'FACEBOOK {post_json}')
        return 'FACEBOOK error parsing json'
        
    return make_fb_call_with_token(post_json_object)

'''
Method called from main class that creates our endpoint request and makes the API call.
Also, prints status of uploading the payload.

@returns: nothing
'''
def post_to_facebook():
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.FACEBOOK,
        post_scheduled_fb_post
    )

def schedule_fb_post( caption, image_query ):
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
    print('FACEBOOK upload scheduled post ressult' + str(result))
    return result
    
def post_blog_promo( blog_title, ref_url ):
    short_url = url_shortener.shorten_tracking_url(
        url_destination=ref_url,
        slashtag='',
        platform=PostingPlatform.FACEBOOK,
        campaign_medium='blog-reference',
        campaign_name=blog_title
    )
    message=gpt.link_prompt_to_string(
        prompt_source_file=os.path.join("src", "input_prompts", "facebook_blog_ref.txt"),
        feedin_title=blog_title,
        feedin_link=short_url
    )
    payload = {
        'link': short_url,
        'message': message, 
        'published' : True
    }
    make_fb_feed_call_with_token(payload)  

def schedule_fb_video_post( caption, remote_video_url ):    
    payload = {
        'media_type': 'VIDEO',
        'url': remote_video_url,
        'message': caption, 
        'published' : True
    }
    result = firebase_storage_instance.upload_scheduled_post(
        PostingPlatform.FACEBOOK, 
        payload
    )
    print('FACEBOOK upload scheduled post ressult' + str(result))
    return result