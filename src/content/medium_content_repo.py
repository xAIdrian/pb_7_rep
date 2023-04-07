import sys
import os
sys.path.append("../src")

import requests
import appsecrets
import utility.text_utils as text_utils
import media.image_creator as image_creator
import ai.gpt as gpt
import json
from storage.firebase_storage import firebase_storage_instance, PostingPlatform

def post_medium_blog_article():
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.MEDIUM,
        post_to_medium,
        is_test=True
    )

def get_user_details():
    url = 'https://api.medium.com/v1/me'
    headers = {
        'Authorization': f'Bearer {appsecrets.MEDIUM_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    elif response.status_code == 401:
        raise Exception('Invalid or revoked access token')
    else:
        raise Exception(f'Request failed with status code {response.status_code}')

def post_to_medium( schedule_datetime_str ):
    post_params_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.MEDIUM, 
        schedule_datetime_str
    )
    try:
        post_params = json.loads(post_params_json)
        title = text_utils.groom_title(post_params['title'])
    except:
        print(f'MD error {post_params_json}')
        return '' 
     
    author_id=get_user_details()['id']

    url = f"https://api.medium.com/v1/users/{author_id}/posts"
    headers = {
        "Authorization": f"Bearer {appsecrets.MEDIUM_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Charset": "utf-8"
    }
    data = {
        "title": title,
        "content": post_params['content'],
        "contentFormat": "html",
        "publishStatus": "public",
        "license": "all-rights-reserved",
        "notifyFollowers": True,
        "canonicalUrl": "https://www.ditchdatingapps.com"
    }
    # if tags:
    #     data["tags"] = tags
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        result = response.json()["data"]
        print(result)
        return result
    else:
        raise Exception(f"MD Error creating post: {response.status_code} - {response.text}") 

def schedule_medium_article(blog):
    try:
        blog = text_utils.groom_body(blog)
        parts = blog.split('\n\n', 1)
        image_src = image_creator.get_unsplash_image_url(
            'female model', 
            PostingPlatform.MEDIUM, 
            'landscape'
        )
        header_img = f'<img src="{image_src}" style="display: block; width: 100%; height: auto;"/><p></p>'

        title = gpt.prompt_to_string(
            prompt_source_file=os.path.join('src', 'input_prompts', 'youtube_title.txt'),
            feedin_source=parts[0]
        )
        title = text_utils.groom_title(title) 
        body = header_img + parts[1]   

        payload = dict()
        payload['title'] = title
        payload['content'] = body
        payload['image'] = dict()
        payload['image']['url'] = image_src
        
        result = firebase_storage_instance.upload_scheduled_post(
            PostingPlatform.MEDIUM, 
            payload
        )
        print(result)
    except Exception as e:
        print(f'Something went wrong parsing blog {e}')    
               