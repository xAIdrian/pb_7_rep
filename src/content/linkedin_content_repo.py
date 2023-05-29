import sys
import os
import json
import requests
import domain.linkedin_auth as li_auth
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
from domain.endpoint_definitions import make_api_call

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

def get_author_from_user(headers):
    '''
        Get user information from Linkedin
    '''
    response = requests.get('https://api.linkedin.com/v2/me', headers = headers)
    user_info = response.json()
    print(f'📦 LI userinfo {user_info}')
    urn = user_info['id']
    return f'urn:li:person:{urn}'

def post_linkedin_link_message():
    #get post from firebase

    credentials = os.path.join('src', 'linkedin_creds.json')
    access_token = li_auth.auth(credentials) # Authenticate the API
    gen_headers = li_auth.headers(access_token) # Make the headers to attach to the API call.

    author = get_author_from_user(gen_headers)
    post_url = 'https://api.linkedin.com/v2/ugcPosts'

    message = '''
        Interested to automate LinkedIn using #Python and the LinkedIn API? 
        Read this in-depth Python for #SEO post I wrote.
    '''
    link = 'https://www.jcchouinard.com/how-to-use-the-linkedin-api-python/'
    link_text = 'Complete tutorial using the LinkedIn API'
    
    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "message"
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": message
                        },
                        "originalUrl": link,
                        "title": {
                            "text": link_text
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
        }
    }
    result = make_api_call(
        post_url, 
        headers=gen_headers,
        req_json=post_data, 
        type='POST'
    )
    print(f'📦 LINKEDIN {result}')
    return result

def post_linkedin_user_message( scheduled_datetime_str ):
    #get post from firebase
    post_params_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.LINKEDIN, 
        scheduled_datetime_str
    )
    try:
        post_params = json.loads(post_params_json)
        print(f'📦 LI post params return {post_params}')
    except:
        print(f'🔥 LI {post_params_json}')
        return '' 

    credentials = os.path.join('src', 'linkedin_creds.json')
    access_token = li_auth.auth(credentials) # Authenticate the API
    gen_headers = li_auth.headers(access_token) # Make the headers to attach to the API call.

    author = get_author_from_user(gen_headers)
    post_url = 'https://api.linkedin.com/v2/ugcPosts'

    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_params['text']
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    result = make_api_call(
        post_url, 
        headers=gen_headers,
        req_json=post_data, 
        type='POST'
    )
    print(f'📦 LI result {result}')
    return result

def post_to_linkedin(is_testmode=False): 
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.LINKEDIN, 
        post_linkedin_user_message,
        is_test = is_testmode
    ) 

def schedule_linkedin_post( text ):

    payload = dict()
    payload['text'] = text
    result = firebase_storage_instance.upload_scheduled_post(
        PostingPlatform.LINKEDIN, 
        payload
    )
    print(f'⏰ LinkedIn scheduled! {result}') 
