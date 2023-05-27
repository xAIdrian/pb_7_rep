import sys
import os
import time
import meta_graph_api.meta_tokens as meta_tokens
from domain.endpoint_definitions import make_api_call
import media.image_creator as image_creator
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import json

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

def create_ig_media_object( params, with_token ):
    """ Create media object

        Args:
            params: dictionary of params
        
        API Endpoint:
            https://graph.facebook.com/v5.0/{ig-user-id}/media?image_url={image-url}&caption={caption}&access_token={access-token}
            https://graph.facebook.com/v5.0/{ig-user-id}/media?video_url={video-url}&caption={caption}&access_token={access-token}

        Returns:
            object: data from the endpoint

    """

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['caption'] = params['caption']  # caption for the post
    if with_token:
        endpointParams['access_token'] = params['access_token']
    endpointParams['published'] = True

    if 'IMAGE' == params['media_type'] : # posting image
        endpointParams['image_url'] = params['media_url']  # url to the asset
    else : # posting video
        endpointParams['media_type'] = params['media_type']  # specify media type
        endpointParams['video_url'] = params['media_url']  # url to the asset
    
    return endpointParams

def schedule_ig_video_post( caption, db_remote_path ):
    
    params = meta_tokens.fetch_personal_access_token() 

    params['media_type'] = 'REELS' 
    params['media_url'] = db_remote_path 
    params['caption'] = caption

    remote_media_obj = create_ig_media_object( params, False )
    upload_result = firebase_storage_instance.upload_scheduled_post(PostingPlatform.INSTAGRAM, remote_media_obj)
    print(f'IG scheduled!\n{upload_result}')

def get_ig_container_status( ig_container_id, params ):
    """ Check the status of a media object

        Args:
            mediaObjectId: id of the media object
            params: dictionary of params
        
        API Endpoint:
            https://graph.facebook.com/v5.0/{ig-container-id}?fields=status_code

        Returns:
            object: data from the endpoint
    """
    url = params['endpoint_base'] + ig_container_id # endpoint url

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['fields'] = 'status_code, status' # fields to get back
    endpointParams['access_token'] = params['access_token'] # access token

    return make_api_call( url=url, req_params=endpointParams, type='GET' ) # make the api call

def publish_media_video_call( post_id, post_params ):
    instagram_id= post_params['instagram_account_id']
    return make_api_call(
        url=f'https://graph.facebook.com/v15.0/{instagram_id}/media_publish', 
        req_params={
            'creation_id': post_id,
            'access_token': post_params['access_token'],
            'debug': 'all'
        }, 
        type='POST'
    )

def publish_image( media_url, post_params, firebase_object):
    post_params['image_url'] = firebase_object['image_url']

    post_response = make_api_call(url=media_url, req_params=post_params, type='POST')
    post_id = post_response['json_data']['id']
    instagram_user_id=post_params['instagram_user_id']

    publish_url = f'https://graph.facebook.com/v15.0/{instagram_user_id}/media_publish'
    publish_params = {
        'creation_id': post_id,
        'access_token': post_params['access_token']
    }
    publish_response = make_api_call(url=publish_url, req_params=publish_params, type='POST')
        
    if publish_response['json_data']['id'] != '':
        print('IG Post published successfully!')
    else:
        print('Error publishing post.')
    return publish_response

# this one worked but went through the FFMPEG process https://dl.dropboxusercontent.com/s/tlyj3rjtc3muu1j/what%20is%20status.mp4
def make_ig_api_call_with_token( firebase_params ):        
    post_params = meta_tokens.fetch_personal_access_token() 

    post_params['caption'] = firebase_params['caption']
    post_params['published'] = firebase_params['published']

    instagram_user_id = post_params['instagram_account_id']
    media_url = post_params['endpoint_base'] + instagram_user_id + '/media'

    if (firebase_params['media_type'] == 'IMAGE'):
        return publish_image(media_url, post_params, firebase_params)

    elif (firebase_params['media_type'] == 'REELS' or firebase_params['media_type'] == 'VIDEO'):
        
        # optimized_url = optimize_video_for_reels_url(firebase_params)
        
        post_params['media_type'] = 'REELS'
        # post_params['video_url'] = optimized_url
        post_params['video_url'] = firebase_params['video_url']
        post_params['published'] = firebase_params['published']
        post_params['share_to_feed'] = True

        post_response = make_api_call(url=media_url, req_params=post_params, type='POST')
        publish_response = monitor_ig_upload_status(
            post_response,
            post_params,
            publish_media_video_call
        )

        if publish_response['json_data']['id'] != '':
            print('IG Post published successfully!')
        else:
            print('Error publishing post.')
        
        return publish_response

def post_scheduled_ig_post( schedule_datetime_str ):
    post_params_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.INSTAGRAM, 
        schedule_datetime_str
    )
    try:
        post_params_json = json.loads(post_params_json)
        print(f'IG firebase fetched {post_params_json}')
    except:
        print(f'IG error {post_params_json}')
        return ''    
    
    return make_ig_api_call_with_token(post_params_json)

# def publish_ig_media( mediaObjectId, params ) :
#     """ Publish content

#         Args:
#             mediaObjectId: id of the media object
#             params: dictionary of params
        
#         API Endpoint:
#             https://graph.facebook.com/v5.0/{ig-user-id}/media_publish?creation_id={creation-id}&access_token={access-token}

#         Returns:
#             object: data from the endpoint
#     """
#     url = params['endpoint_base'] + params['instagram_account_id'] + '/media_publish' # endpoint url

#     endpointParams = dict() # parameter to send to the endpoint
#     endpointParams['creation_id'] = mediaObjectId # fields to get back
#     endpointParams['access_token'] = params['access_token'] # access token

#     return make_api_call( url=url, req_params=endpointParams, type='POST' ) # make the api call

def post_ig_media_post(is_testmode=False):
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.INSTAGRAM,
        post_scheduled_ig_post,
        is_test = is_testmode
    )

def schedule_ig_image_post( caption, image_query ):
    '''
    Method called from main class that creates our endpoint request and makes the API call.

    @returns: nothing
    '''
    params = meta_tokens.fetch_personal_access_token() 
    params['media_type'] = 'IMAGE' 
        
    params['media_url'] = image_creator.get_unsplash_image_url(image_query, PostingPlatform.INSTAGRAM) 
    params['caption'] = caption
        
    remote_media_obj = create_ig_media_object( params, False ) 
    firebase_storage_instance.upload_scheduled_post(PostingPlatform.INSTAGRAM, remote_media_obj)

def monitor_ig_upload_status( ig_upload_response, post_params, publish_func ):	
    upload_container_id = ig_upload_response['json_data']['id'] # id of the media object that was created
    container_status_code = 'IN_PROGRESS'

    print(f"\nIG upload container {upload_container_id} beginning upload") # id of the object

    while container_status_code != 'FINISHED': # keep checking until the object status is finished
        container_status_response = get_ig_container_status( upload_container_id, post_params ) # check the status on the object
        container_status_code = container_status_response['json_data']['status_code'] # update status code
        if (container_status_code == 'ERROR'): 
            print(container_status_response['json_data']['status'])
            break

        print(f"Status Code: {container_status_code.lower()}") # status code of the object
        time.sleep( 5 ) # wait 5 seconds if the media object is still being processed

    publish_container_response = publish_func( upload_container_id, post_params ) # publish the post to instagram
    print(f"IG upload complete {publish_container_response['json_data']['id']}") # json response from ig api
    return publish_container_response

def get_content_publishing_limit( params ) :
    """ Get the api limit for the user

        Args:
            params: dictionary of params
        
        API Endpoint:
            https://graph.facebook.com/v5.0/{ig-user-id}/content_publishing_limit?fields=config,quota_usage

        Returns:
            object: data from the endpoint
    """
    url = params['endpoint_base'] + params['instagram_account_id'] + '/content_publishing_limit' # endpoint url

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['fields'] = 'config,quota_usage' # fields to get back
    endpointParams['access_token'] = params['access_token'] # access token

    return make_api_call( url=url, req_params=endpointParams, type='GET' ) # make the api call
