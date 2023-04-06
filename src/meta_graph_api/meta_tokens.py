import sys
import os
sys.path.append("../src")

from domain.endpoint_definitions import make_api_call
import requests
import appsecrets
import json
from storage.firebase_storage import firebase_storage_instance, PostingPlatform

def create_fb_credentials_object():
	""" 
        Get creds required for use in the applications
	
        @return:
            dictonary: credentials needed globally
	"""

	creds = dict() # dictionary to hold everything
	creds['access_token'] = firebase_storage_instance.get_meta_short_lived_token(PostingPlatform.FACEBOOK) # access token for use with all api calls
	creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
	creds['graph_version'] = 'v15.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
	creds['debug'] = 'no'

	return creds	

def create_personal_credentials_object():
	""" 
        Get creds required for use in the applications
        
        @returns:
            dictonary: credentials needed globally
	"""
	creds = dict() # dictionary to hold everything
	creds['access_token'] = firebase_storage_instance.get_meta_short_lived_token(PostingPlatform.INSTAGRAM) # access token for use with all api calls
	creds['client_id'] = appsecrets.META_APP_ID
	creds['client_secret'] = appsecrets.META_APP_SECRET
	creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
	creds['graph_version'] = 'v15.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
	creds['instagram_account_id'] = appsecrets.INSTAGRAM_GRAPH_API_PAGE_ID # users instagram account id
	creds['debug'] = 'no'

	return creds

def fetch_personal_access_token() :
    """ 
        Get long lived access token
        
        API Endpoint:
            https://graph.facebook.com/{graph-api-version}/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={your-access-token}
        @returns:
            object: data from the endpoint
    """
    params = create_personal_credentials_object()
    cachedToken = firebase_storage_instance.get_meta_bearer_token(PostingPlatform.INSTAGRAM)

    if (cachedToken != ''):
        params['access_token'] = cachedToken
        print(f"IG found cached token!")
        return params
    else:
        token_params = dict() # parameter to send to the endpoint
        token_params['grant_type'] = 'fb_exchange_token' # tell facebook we want to exchange token
        token_params['client_id'] = params['client_id'] # client id from facebook app
        token_params['client_secret'] = params['client_secret'] # client secret from facebook app
        token_params['fb_exchange_token'] = params['access_token'] # access token to get exchange for a long lived token

        token_url = params['endpoint_base'] + 'oauth/access_token' # endpoint url
        token_response = make_api_call( url=token_url, params=token_params, type=params['debug'] ) # make the api call
        
        pretty_dump = json.dumps( token_response['json_data'], indent = 4 ) 
        print(pretty_dump)

        access_token = token_response['json_data']['access_token']
        firebase_storage_instance.store_meta_bearer_token(PostingPlatform.INSTAGRAM, access_token)

        params['access_token'] = access_token

    return params

def make_page_access_token_request():
    '''
        Construct the object and get the actual long lived access token. Store the token
        To be specific, this is using the short lived token to get the long lived token

        @returns:
            dict: complete params including the access token for future requests
    '''
    print('FB creating an entirely new token using short-lived')

    # construct our base request params used throughout
    params = create_fb_credentials_object()
    post_url = params['endpoint_base'] + appsecrets.FACEBOOK_GRAPH_API_PAGE_ID
        
    params['fields'] = 'access_token'
    params['access_token'] = params['access_token']

    # make api call to get long lived token with short lived token
    response = make_api_call( url=post_url, req_params=params, type='GET' )
    print(response['json_data_pretty'])

    # access new access token and store remotely
    params['page_access_token'] = response['json_data']['access_token']
    firebase_storage_instance.store_meta_bearer_token(PostingPlatform.FACEBOOK, params['page_access_token'])
    
    return params

def refresh_fb_page_access_token( existing_access_token ):
    '''
        Check and refresh the Facebook Page Access Token when expired or about to expire.
        To be specific, this is using the long lived token to get another long lived token

        @param: 
            old_token: str, the current Facebook Page Access Token
        @returns: 
            str: the new long-lived Facebook Page Access Token. Empty strings if erros arise
    '''
    # Check the state of the existing access token
    debug_token_url = f'https://graph.facebook.com/v12.0/debug_token?input_token={existing_access_token}&access_token={appsecrets.META_APP_ID}|{appsecrets.META_APP_SECRET}'

    print(f'FB checking the validity of cached token')
    debug_token_response = requests.get(debug_token_url)

    if debug_token_response.status_code == 200:
        data = json.loads(debug_token_response.text)
        is_valid = data['data']['is_valid']
        expires_at = data['data']['expires_at']
        if not is_valid:
            raise ValueError('The existing access token is not valid')
    else:
        raise ValueError('Error while checking the existing access token')

    # Parse the response for error
    # If the key exists in the dictionary, it will return the corresponding value. If the key does not exist, it will return None.
    error = data.get('error')
    if error is not None:
        raise ValueError(f'Error in response: {error["message"]}')

    # Get the new long-lived access token
    print('FB making request to update our existing long lived token')
    exchange_token_url = f'https://graph.facebook.com/v12.0/oauth/access_token?grant_type=fb_exchange_token&client_id={appsecrets.META_APP_ID}&client_secret={appsecrets.META_APP_SECRET}&fb_exchange_token={existing_access_token}'
    exchange_token_response = requests.get(exchange_token_url)

    if exchange_token_response.status_code == 200:
        data = json.loads(exchange_token_response.text)
        new_access_token = data['access_token']
        
        # Store the new
        firebase_storage_instance.store_meta_bearer_token(PostingPlatform.FACEBOOK, new_access_token)

        return new_access_token
    else:
        raise ValueError('Error while getting the new access token')

def fetch_fb_page_access_token():
    '''
        Conditional housing to create the params objects for subsequent requests.
        We fetch them from Firebase and make API to fetch a fresh token if conditions are right.
    
        @returns:
            dict: Complete params including the access token for future requests    
    '''
    cachedToken = firebase_storage_instance.get_meta_bearer_token(PostingPlatform.FACEBOOK)

    if (cachedToken != ''):
        params = dict()
        params['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
        params['graph_version'] = 'v15.0' # version of the api we are hitting
        params['endpoint_base'] = params['graph_domain'] + params['graph_version'] + '/'
        params['page_access_token'] = refresh_fb_page_access_token(cachedToken)
        return params
    else:
        return make_page_access_token_request()

