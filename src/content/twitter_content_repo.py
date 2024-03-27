import sys
import os
import tweepy
import appsecrets
from storage.firebase_storage import firebase_storage_instance, PostingPlatform
import json
import ai.gpt as gpt
import domain.url_shortener as url_shortener
import requests
import media.image_creator as image_creator
import storage.dropbox_storage as dropbox_storage

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

def initialize_tweepy():
    # Authenticate to Twitter
    # MUST upgrade to oauth2handler https://docs.tweepy.org/en/stable/authentication.html
    auth = tweepy.OAuthHandler(appsecrets.TWITTER_API_KEY, appsecrets.TWITTER_API_SECRET)
    auth.set_access_token(appsecrets.TWITTER_API_AUTH_TOKEN, appsecrets.TWITTER_API_AUTH_SECRET)

    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        print("TWeepy init OK")
    except:
        print("🔥 Error during Tweepy authentication") 
    return api    

tweepy_api = initialize_tweepy()

def update_tweet( text ):
    try:
        value = tweepy_api.update_status(status = text)  
        return value
    except Exception as e:
        print(f'🔥 TW {e}')
        return None

def update_tweet_with_video ( db_remote_path, tweet ):
    local_path = dropbox_storage.download_file_to_local_path(db_remote_path)
    with open(local_path, 'rb') as f:
        print('🌐 Uploading twitter video...')
        media = tweepy_api.media_upload(
            filename=os.path.basename(local_path), 
            file=f,
            chunked=True, 
            wait_for_async_finalize=True,
            media_category='tweet_video'
        )
        print('🌐 Video uploaded!' + str(media) + '...')
        if (len(tweet) > 275): tweet = 'Exclusive mentorship deal is only available TODAY.  Click the link in our bio to instantly learn how you can stop wasting time on dating apps and have a fulfilling dating life!'
        tweet = tweepy_api.update_status(status=tweet, media_ids=[media.media_id])
    return tweet

def update_tweet_with_image(url, tweet):
    local_filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(local_filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        result = tweepy_api.update_status_with_media(filename=local_filename, status=tweet)
        os.remove(local_filename)
        return result
    else:
        print("🔥 Unable to download image")
        return None
    
# def post_blog_promo_tweet( blog_title, ref_url ):
#     short_url = url_shortener.shorten_tracking_url(
#         url_destination=ref_url,
#         slashtag='',
#         platform=PostingPlatform.TWITTER,
#         campaign_medium='blog-reference',
#         campaign_name=blog_title
#     )
#     text=gpt.link_prompt_to_string(
#         prompt_source_file=os.path.join("src", "input_prompts", "twitter_blog_ref.txt"),
#         feedin_title=blog_title,
#         feedin_link=short_url
#     )
#     update_tweet(text)

def post_scheduled_tweet( scheduled_datetime_str ):
    '''
        Our strict interaction with the Tweepy API

        @params:

        @returns:
            value: with success. this is the post response
            none: with error.
    '''
    post_params_json = firebase_storage_instance.get_specific_post(
        PostingPlatform.TWITTER, 
        scheduled_datetime_str
    )
    try:
        post_params = json.loads(post_params_json)
        print(f'📦 TW post params return {post_params}')
    except:
        print(f'🔥 TW {post_params_json}')
        return ''  
            
    tweet = post_params['tweet']
    if ('media_url' in post_params):
        media_url = post_params['media_url']
        if (media_url != ''):
            return update_tweet_with_video(media_url, tweet)
    return update_tweet(tweet)

def post_tweet(is_testmode=False): 
    return firebase_storage_instance.upload_if_ready(
        PostingPlatform.TWITTER, 
        post_scheduled_tweet,
        is_test = is_testmode
    )

def schedule_video_tweet( tweet, video_remote_url ):
    if (video_remote_url != '' and tweet != ''):
        payload = dict()
        payload['tweet'] = tweet
        payload['media_url'] = video_remote_url
        result = firebase_storage_instance.upload_scheduled_post(
            PostingPlatform.TWITTER, 
            payload
        )
        print(f'⏰ Tweet scheduled!\n{result}')  
    else:
        print('🔥 Error scheduling TW')
        return ''
    

def schedule_tweet( tweet ):
    if (tweet != ''):
        payload = dict()
        payload['tweet'] = tweet

        result = firebase_storage_instance.upload_scheduled_post(
            PostingPlatform.TWITTER, 
            payload
        )
        print(f'⏰ Tweet scheduled!\n{result}') 
    else:
        print('🔥 Error scheduling TW')
        return ''    
