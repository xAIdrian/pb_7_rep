import sys
sys.path.append("../src")

import json
import appsecrets
import requests
import string
import random
import utility.utils as utils

api_url = 'https://www.linkedin.com/oauth/v2'

def read_creds(filename):
    '''
    Store API credentials in a safe place.
    If you use Git, make sure to add the file to .gitignore
    '''
    with open(filename) as f:
        credentials = json.load(f)
    return credentials
 
def create_CSRF_token():
    '''
        This function generates a random string of letters.
        It is not required by the Linkedin API to use a CSRF token.
        However, it is recommended to protect against cross-site request forgery
    '''
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token

def authorize( api_url, client_id, client_secret, redirect_uri ):
    '''
    Make a HTTP request to the authorization URL.
    It will open the authentication URL.
    Once authorized, it'll redirect to the redirect URI given.
    The page will look like an error. but it is not.
    You'll need to copy the redirected URL.
    '''
    # Request authentication URL
    csrf_token = create_CSRF_token()
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': csrf_token,
        'scope': 'r_liteprofile,r_emailaddress,w_member_social'
        }
 
    response = requests.get(f'{api_url}/authorization',params=params)
 
    print(f'''
        The Browser will open to ask you to authorize the credentials.\n
        Since we have not set up a server, you will get the error:\n
        This site can’t be reached. localhost refused to connect.\n
        This is normal.\n
        You need to copy the URL where you are being redirected to.\n
    ''')
 
    utils.open_url(response.url)
 
    # Get the authorization verifier code from the callback url
    redirect_response = input('Paste the full redirect URL here:')
    auth_code = utils.parse_redirect_uri(redirect_response)
    return auth_code

def refresh_token(auth_code,client_id,client_secret,redirect_uri):
    '''
    Exchange a Refresh Token for a New Access Token.
    '''
    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
 
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
        }
 
    response = requests.post(access_token_url, data=data, timeout=30)
    response = response.json()
    print(response)
    access_token = response['access_token']
    return access_token
 
# if __name__ == '__main__':
#     credentials = 'credentials.json'
#     access_token = auth(credentials)

def auth(credentials):
    '''
    Run the Authentication.
    If the access token exists, it will use it to skip browser auth.
    If not, it will open the browser for you to authenticate.
    You will have to manually paste the redirect URI in the prompt.
    '''
    creds = read_creds(credentials)
    client_id, client_secret = creds['client_id'], creds['client_secret']
    redirect_uri = creds['redirect_uri']
         
    if 'access_token' not in creds.keys(): 
        args = client_id,client_secret,redirect_uri
        auth_code = authorize(api_url,*args)
        access_token = refresh_token(auth_code,*args)
        creds.update({'access_token':access_token})
        utils.save_token(credentials, creds)
    else: 
        access_token = creds['access_token']
    return access_token

def headers(access_token):
    '''
        Make the headers to attach to the API call.
    '''
    headers = {
    'Authorization': f'Bearer {access_token}',
    'cache-control': 'no-cache',
    'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers