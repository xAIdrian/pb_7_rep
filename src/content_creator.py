from __future__ import unicode_literals

import sys
import os
sys.path.append("../src")

import ai.gpt as gpt
import storage.dropbox_storage as dropbox_storage
import content.ig_content_repo as ig_content_repo
import content.fb_content_repo as fb_content_repo
import content.shopify_content_repo as shopify_content_repo
import content.twitter_content_repo as twitter_content_repo
import content.youtube_content_repo as youtube_content_repo
import media.video_downloader as video_processor
import storage.google_drive_storage as google_drive

CLIENT_SECRET_FILE='ai-content-machine-d8dcc1434069.json'

# Begin the running of our application
if __name__ == '__main__':

    # Quickly process our posts
    # put our post calls here. this will need to be first with the proper implementation
    # post('Shopify', shopify_content_repo.post_shopify_blog_article())
    # post('Facebook', fb_content_repo.post_fb_image())
    # post('Instagram', ig_content_repo.post_ig_media_post())
    # post('Twitter', twitter_content_repo.post_tweet())

    local_joined_path = os.path.join('src','output_downloads')
    db_remote_url = dropbox_storage.get_file_path_for_earliest_ready_short_video()

    if (db_remote_url is not None and db_remote_url != ''):
        # strip mp3 to generate text
        # local_audio_path = video_processor.save_to_mp3(db_remote_url)
        # transcript_path = gpt.mp3_to_transcript(local_audio_path)
        # summary_output_path = gpt.transcript_to_summary(transcript_path)

        # works
        # youtube_content_repo.complete_scheduled_post_youtube_video(
        #     remote_video_url=db_remote_url
        # )

        # works
        # gpt.generate_video_with_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'instagram.txt'),
        #     remote_video_url=db_remote_url,
        #     upload_func=ig_content_repo.schedule_ig_video_post
        # )
        # ig_content_repo.post_ig_media_post()

        # works
        # gpt.generate_video_with_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'facebook.txt'),
        #     remote_video_url=db_remote_url,
        #     upload_func=fb_content_repo.schedule_fb_video_post
        # )
        # fb_content_repo.post_to_facebook()

        # Text Content
        # # TWEETS
        # gpt.generate_video_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
        #     video_meta_data='',
        #     should_polish_post=True,
        #     post_num=8,
        #     upload_func=twitter_content_repo.schedule_tweet
        # )
                 
        # FACEBOOK 
        # gpt.generate_video_prompt(
        #     prompt_source = os.path.join('src', 'input_prompts', 'facebook.txt'),
        #     image_query_term = content_description, 
        #     should_polish_post=True,
        #     post_num=1,
        #     upload_func = fb_content_repo.schedule_fb_post
        # )
    #             # INSTAGRAM
    #             gpt.generate_prompt_response(
    #                 prompt_source=os.path.join('src', 'input_prompts', 'instagram.txt'),
    #                 image_query_term=content_description,
    #                 should_polish_post=True,
    #                 post_num=2,
    #                 upload_func=ig_content_repo.schedule_ig_image_post
    #             )
    #             # BLOG AND PROMOS
    #             gpt.generate_prompt_response(
    #                 prompt_source=os.path.join('src', 'input_prompts', 'blog.txt'),
    #                 image_query_term=content_description,
    #                 should_polish_post=False,
    #                 post_num=1,
    #                 upload_func=shopify_content_repo.schedule_shopify_blog_article
    #             )
    #             # TWEETS
    #             gpt.generate_prompt_response(
    #                 prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
    #                 image_query_term=content_description,
    #                 should_polish_post=True,
    #                 post_num=16,
    #                 upload_func=twitter_content_repo.schedule_tweet
    #             )
    #         except Exception as e:
    #             print(f'Finished with error {e}')        
    # print('Finished and completed')
    