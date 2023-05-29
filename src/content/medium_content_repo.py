import sys
import os
import requests
import appsecrets
import utility.text_utils as text_utils
import media.image_creator as image_creator
import ai.gpt as gpt
import json
from storage.firebase_storage import firebase_storage_instance, PostingPlatform

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

def post_to_medium(is_testmode=False):
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.MEDIUM,
        post_medium_blog_article,
        is_test = is_testmode
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

def post_medium_blog_article( schedule_datetime_str ):
    post_params_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.MEDIUM, 
        schedule_datetime_str
    )
    try:
        post_params = json.loads(post_params_json)
        title = text_utils.groom_title(post_params['title'])
    except:
        print(f'🔥 MD error {post_params_json}')
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
        "title": title.replace('"', ''),
        "content": post_params['content'],
        "contentFormat": "html",
        "publishStatus": "public",
        "license": "all-rights-reserved",
        "notifyFollowers": True,
        "canonicalUrl": "t.me/+GAtVkGVft8cwMTYx"
    }
    # if tags:
    #     data["tags"] = tags
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        result = response.json()["data"]
        print(f'📦 MD result{result}')
        return result
    else:
        print(f"🔥 MD Error creating post: {response.status_code} - {response.text}") 

def schedule_medium_article(blog):
    try:
        blog = text_utils.groom_body(blog)
        parts = blog.split('\n\n', 1)
        image_src = image_creator.get_unsplash_image_url(
            'technology', 
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
        
        result = firebase_storage_instance.upload_scheduled_post(
            PostingPlatform.MEDIUM, 
            payload
        )
        print(f'📦 MD result {result}')
    except Exception as e:
        print(f'🔥 MD: Something went wrong parsing blog {e}')        

#construct and save address of uploaded blog
                # if (result):
                #     base_path = "https://www.caregivermodern.com/blogs/caregiver-help-how-to/"
                #     updated_title = new_article.title.replace(' ', '-').replace('\'', '').replace(',','').replace('.', '').replace('"', '').replace(':','')
                #     combined_url = base_path + updated_title
                        
                #     twitter_content_repo.post_blog_promo_tweet(
                #         blog_title=new_article.title,
                #         ref_url=combined_url
                #     )
                #     fb_content_repo.post_blog_promo(
                #         blog_title=new_article.title,
                #         ref_url=combined_url
                #     )        
