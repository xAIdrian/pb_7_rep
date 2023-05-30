import sys
import appsecrets as appsecrets
import requests
import json
import os
from storage.firebase_storage import PostingPlatform

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

# "raw": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d",
# "full": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg",
# "regular": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg&w=1080&fit=max",
# "small": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg&w=400&fit=max",
# "thumb": "https

def get_unsplash_image_url( search_query, platform, orientation = 'portrait' ):
    if(platform == PostingPlatform.FACEBOOK):
        resolution_key='regular'
    elif(platform == PostingPlatform.INSTAGRAM):
        resolution_key='regular'
    elif(platform == PostingPlatform.TWITTER):
        resolution_key='regular'
    elif(platform == PostingPlatform.MEDIUM):
        resolution_key='regular'    
    elif(platform == PostingPlatform.YOUTUBE):
        resolution_key='full'
    else:
        resolution_key='regular'        

    url = 'https://api.unsplash.com/photos/random'
    params = {
        'query': search_query,
        'orientation': orientation
    }
    headers = {
        'Accept-Version': "v1",
        'Authorization': 'Client-ID ' + appsecrets.UNSPLASH_ACCESS_KEY
    }
    response = requests.get( 
        url = url, 
        params = params,
        headers = headers
    )
    try:
        json_content = json.loads( response.content )
        if (json_content['urls'] is not None):
            result_url=json_content['urls'][resolution_key]
            return result_url
        else:
            return ''
    except:
        print(f'error with image {response}')
        return ''
