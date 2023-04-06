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
import content.linkedin_content_repo as linkedin_content_repo

CLIENT_SECRET_FILE='ai-content-machine-d8dcc1434069.json'

# Begin the running of our application
if __name__ == '__main__':

    # Quickly process our posts

    # ig_content_repo.post_ig_media_post()
    # fb_content_repo.post_to_facebook()
    # twitter_content_repo.post_tweet()

    # Get newest video from Dropbox and create content

    local_joined_path = os.path.join('src','output_downloads')
    db_video_entry = dropbox_storage.get_earliest_ready_short_video()

    db_path = db_video_entry.path_display
    # db_stream_url = dropbox_storage.get_streaming_download_url(db_video_entry.path_display)

    if (db_path is not None and db_path != ''):
        # strip mp3 to generate text
        # local_audio_path = video_processor.save_to_mp3(db_remote_url)
        # transcript_path = gpt.mp3_to_transcript(local_audio_path)
        # summary_output_path = gpt.transcript_to_summary(transcript_path)

        # Youtube Shorts
        # youtube_content_repo.complete_scheduling_and_posting_of_video(
        #     db_remote_path=db_path
        # )

        # Instagram Reels
        # gpt.generate_video_with_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'instagram.txt'),
        #     db_remote_path=db_path,
        #     upload_func=ig_content_repo.schedule_ig_video_post
        # )
        # ig_content_repo.post_ig_media_post()

        # Facebook Page & Personal
        # gpt.generate_video_with_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'facebook.txt'),
        #     db_remote_path=db_path,
        #     upload_func=fb_content_repo.schedule_fb_video_post
        # )
        # fb_content_repo.post_to_facebook()

        # Twitter 
        # gpt.generate_video_with_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
        #     db_remote_path=db_path,
        #     upload_func=twitter_content_repo.schedule_video_tweet
        # )
        # gpt.generate_text_prompt(
        #     prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
        #     post_num=8,
        #     upload_func=twitter_content_repo.schedule_tweet,
        #     should_polish=True
        # )
        # twitter_content_repo.post_tweet()
                 
        # dropbox_storage.move_file(db_path, '/ContentUploaded/' + os.path.basename(db_path))
   
    #             # BLOG AND PROMOS
    #             gpt.generate_prompt_response(
    #                 prompt_source=os.path.join('src', 'input_prompts', 'blog.txt'),
    #                 image_query_term=content_description,
    #                 should_polish_post=False,
    #                 post_num=1,
    #                 upload_func=shopify_content_repo.schedule_shopify_blog_article
    #             )
    #             # TWEETS
    #             
    #         except Exception as e:
    #             print(f'Finished with error {e}')        
    print('Finished and completed')
    