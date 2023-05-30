import sys
import os
import requests
import json
import appsecrets
from storage.firebase_storage import PostingPlatform
import domain.endpoint_definitions as endpoint_definition

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

rebrandly_url = "https://api.rebrandly.com/v1/links"

def shorten_tracking_url( url_destination, slashtag, platform, campaign_medium, campaign_name ):
    '''
        Makes a web request to get a shortened URL and gives you back the result.
    '''
    campaign_name = campaign_name.replace(' ', '+')
    final_url = f'{url_destination}?utm_source={platform.value}&utm_medium={campaign_medium}&utm_campaign={campaign_name}'

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "apikey": appsecrets.REBRANDLY_API_KEY
    }
    json_payload = {
        "destination": final_url
    }
    response = endpoint_definition.make_api_call(
        url=rebrandly_url,
        headers=headers,
        req_json=json_payload,
        type='POST'
    )
    short_url=response['json_data']['shortUrl']
    print(short_url)
    return short_url
