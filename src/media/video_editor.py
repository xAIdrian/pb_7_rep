import sys
import os
sys.path.append("../src")

import requests
import json
import appsecrets as appsecrets
import utility.utils as utils
import media.image_creator as image_creator
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import ai.speech_synthesis as speech_synthesis
import time
import constants

movies_url = 'https://api.json2video.com/v2/movies'

def get_edited_movie_url( uploaded_project_id ):
    '''
    Polls to get our movie response. Repeatedly pining off the server until we get the response we want.

    @returns: remote movie url
    '''
    # status states: not started, done, in progress
    video_upload_status='not started'

    params = dict()
    params['project'] = uploaded_project_id
    headers = dict()
    headers['x-api-key'] = appsecrets.JSON_TO_VIDEO_API_KEY

    while (video_upload_status != 'done'):
        response = requests.get( 
            url = movies_url, 
            params = params, 
            headers = headers 
        )
        video_upload_status = get_response_status_check(response)
        if (video_upload_status == 'error'):
            return "no movie url"
        time.sleep(25)

    movie_url = get_response_movie_url(response)
    return movie_url

def get_simple_scene_images( image_query, scene_array ):
    images = []
    for scene in scene_array:
        new_image = image_creator.get_unsplash_image_url(image_query, PostingPlatform.YOUTUBE)
        images.append(new_image)
    return images    

def edit_movie_for_remote_url ( image_query ):
    '''
    Send the request to get create our movie programmatically.

    WARNING: This influences our quota

    We pull the data from files.  To create our video scenes.
    Then we poll the get request until the video is ready, giving us the url.

    @returns: remote URL for our video
    '''
    # setting up the request
    post_headers = {
        'x-api-key': appsecrets.JSON_TO_VIDEO_API_KEY
    }

    # preparing the pieces
    # scene_images = get_scene_images_array(image_query)
    
    file_path = os.path.join("src", "outputs", "story_output.txt")
    story_text = utils.open_file(file_path)
    speech_bundle = speech_synthesis.text_to_speech(story_text)
    # speech_bundle = {'speech_duration': 96.8125, 'speech_remote_path': 'ai_content_machine/speech_to_text.mp3'}
    print(speech_bundle)
    if (speech_bundle['speech_duration'] > 60): 
        speech_bundle['speech_duration'] = 60

    video_json = create_video_json(
        image_query=image_query,
        mp3_duration = speech_bundle['speech_duration'],
        mp3_remote_path = speech_bundle['speech_remote_path']
    )
    response = requests.post(
        url = movies_url, 
        json = video_json, 
        headers = post_headers
    )
    project_id = post_response_project_id(response)

    if (project_id != -1):
        print(f'\nproject id {project_id}\n')
        movie_url = get_edited_movie_url(project_id)
        # if (movie_url != ''): firebase_storage_instance.delete_storage_file(speech_bundle['speech_remote_path'])
        return movie_url
    else:
        print('error processing project id')
        return ''

#--------------- Preparing The Pieces -----------------------------------------------------    
'''
Generates our AI images for the video we are creating.

WARNING: This procedure costs money.  Use a dummy list where possible.

@returns: array of image urls
'''
def get_scene_images_array(image_query):
    print('get images array')
    images = []

    file_path = os.path.join("src", "output_story_scenes", "mjv4_output.txt")
    promptfile = open(file_path, 'r')
    prompts = promptfile.readlines()
    print(f'\npromptfile\n {promptfile}\n')

    for prompt in prompts:
        if (prompt != ''):
            print(f'prompt: {prompt}')
            image = image_creator.get_ai_image(prompt)
            images.append(image)

    return images    

# TODO we need a parameter for draft, this is submitted with the job
def create_video_json( image_query, mp3_duration, mp3_remote_path ):
    '''
    Dynamically generates our movie json for generation using supplied arguments.
    Transitions, inclusions of audio, and quality are hard-coded.

    @returns: json formatted string
    '''
    if (isinstance(mp3_duration, str)):
        return "error: mp3_duration is not a number"

    scene_comments = get_scene_comment_array()
    image_array = get_simple_scene_images(image_query, scene_comments)

    scene_duration = mp3_duration / len(image_array)
    mp3_ref_url = firebase_storage_instance.get_url(mp3_remote_path)
    print(f'processing mp3 of duration: {mp3_duration} and {len(image_array)} images')

    video_params = {
        "resolution": 'instagram-story',
        "quality": "high",
        "draft": True,
        "elements": [
            {
                "type": "audio",
                "src": mp3_ref_url,
                "volume": 1,
                "duration": -1
            }
        ],
        "scenes": []
    }

    for image in image_array:
        scene = {
            "transition": {
                "style": "fade",
                "duration": 1.5
            },
            "elements": [
                {
                    "type": "image",
                    "src": image,
                    "duration": scene_duration,
                    "scale": {
                        "height":constants.VIDEO_IMAGE_HEIGHT,
                        "width": constants.VIDEO_IMAGE_WIDTH
                    }
                }
            ] 
        }
        video_params['scenes'].append(scene)
    return video_params

'''
Simply reads from our file system to get the description of scenes created by ChatGPT

@returns: array of strings
'''
def get_scene_comment_array():
    folder_path = os.path.join("src", "output_story_scenes")
    return [
        utils.open_file(os.path.join(folder_path, 'scene1.txt')),
        utils.open_file(os.path.join(folder_path, 'scene2.txt')),
        utils.open_file(os.path.join(folder_path, 'scene3.txt')),
        utils.open_file(os.path.join(folder_path, 'scene4.txt')),
        utils.open_file(os.path.join(folder_path, 'scene5.txt')),
        utils.open_file(os.path.join(folder_path, 'scene6.txt')),
        utils.open_file(os.path.join(folder_path, 'scene7.txt')),
        utils.open_file(os.path.join(folder_path, 'scene8.txt')),
        utils.open_file(os.path.join(folder_path, 'scene9.txt')),
        utils.open_file(os.path.join(folder_path, 'scene10.txt'))
    ]


#--------------- Display Status -----------------------------------------------------------
'''
Extracts the response status assuming a success response

@returns: status string
'''
def get_response_status_check( data ):
    response = dict()
    response['json_data'] = json.loads( data.content ) # response data from the api
    response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

    print(response['json_data_pretty'])

    status = response['json_data']['movie']['status']

    print(f"Pinging Status...{status}")
    
    return status

'''
Extracts the response url assuming a success response

@returns: remote url for our created video
'''
def get_response_movie_url( data ) :
    response = dict()
    response['json_data'] = json.loads( data.content ) # response data from the api
    response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

    movie_url = response['json_data']['movie']['url']

    print(f"\nMovie url: {movie_url}")
    
    return movie_url

'''
Extracts the response status assuming a success response

@returns: project id string
'''
def post_response_project_id( data ) :
    response = dict()
    response['json_data'] = json.loads( data.content ) # response data from the api
    response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

    print(response['json_data_pretty'])
    response['success'] = response['json_data']['success']

    if (response['success'] == True):
        response['project_id'] = response['json_data']['project']
        response['timestamp'] = response['json_data']['timestamp']
        return response['project_id']
    else:    
        response['message'] = response['json_data']['message']
        response['timestamp'] = response['json_data']['timestamp']
        return -1

# --------------- Dummy Code -----------------------------

example_of_running_movie_generation = {
    "success": "true",
    "movie": {
        "success": 'false',
        "status": "running",
        "message": "downloading assets",
        "project": "pQNF8AablTeqEMWb",
        "url": 'null',
        "created_at": "2023-02-08T10:52:57.636Z",
        "ended_at": 'null',
        "draft": 'false',
        "rendering_time": 'null'
    },
    "remaining_quota": {
        "movies": 14,
        "drafts": 37
    }
}

example_video = {
    "resolution": "full-hd",
    "quality": "high",
    "scenes": [
        {
            "comment": "Scene #1",
            "transition": {
                "style": "circleopen",
                "duration": 1.5
            },
            "elements": [
                {
                    "type": "image",
                    "src": "https://assets.json2video.com/assets/images/london-01.jpg",
                    "duration": 10
                }, 
                {
                    "type": "audio",
                    "src": "https://assets.json2video.com/assets/audios/thunder-01.mp3"
                }
            ]
        },
        {
            "comment": "Scene #2",
            "transition": {
                "style": "wipeup",
                "duration": 1.5
            },
            "elements": [
                {
                    "type": "image",
                    "src": "https://assets.json2video.com/assets/images/london-02.jpg",
                    "duration": 10
                }
            ]
        },
        {
            "comment": "Scene #3",
            "transition": {
                "style": "fade",
                "duration": 1.5
            },
            "elements": [
                {
                    "type": "image",
                    "src": "https://assets.json2video.com/assets/images/london-03.jpg",
                    "duration": 10,
                    "scale": {
                        "height":constants.VIDEO_IMAGE_HEIGHT,
                        "width": constants.VIDEO_IMAGE_WIDTH
                    }
                }
            ]
        }
    ]
}    
