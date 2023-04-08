from __future__ import unicode_literals

import sys
import os
sys.path.append("../src")

import ai.gpt as gpt
import storage.dropbox_storage as dropbox_storage
import content.ig_content_repo as ig_content_repo
import content.fb_content_repo as fb_content_repo
import content.twitter_content_repo as twitter_content_repo
import content.youtube_content_repo as youtube_content_repo
import content.linkedin_content_repo as linkedin_content_repo
import content.medium_content_repo as medium_content_repo
import media.video_converter as video_converter

CLIENT_SECRET_FILE='ai-content-machine-d8dcc1434069.json'

# Begin the running of our application
if __name__ == '__main__':
    # Quickly process our post calls
    # ig_content_repo.post_ig_media_post()
    # fb_content_repo.post_to_facebook()
    # twitter_content_repo.post_tweet()
    # medium_content_repo.post_to_medium()
    # linkedin_content_repo.post_to_linkedin()

    dropbox_storage.bulk_download_prompts()
    # Get newest video from Dropbox and create content
    local_joined_path = os.path.join('src','output_downloads')
    db_video_entry = dropbox_storage.get_earliest_ready_short_video()

    db_remote_path = db_video_entry.path_display

    if (db_remote_path is not None and db_remote_path != ''):
        local_audio_path = video_converter.local_video_to_mp3(
            dropbox_storage.download_file_to_local_path(db_remote_path)
        )
        transcript_path = gpt.mp3_to_transcript(local_audio_path)
        summary_output_path = gpt.transcript_to_summary(transcript_path)

        # Youtube Shorts
        youtube_content_repo.complete_scheduling_and_posting_of_video(
            db_remote_path=db_remote_path
        )

        # Instagram Reels
        gpt.generate_video_with_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'instagram.txt'),
            db_remote_path=db_remote_path,
            upload_func=ig_content_repo.schedule_ig_video_post
        )

        # Facebook Page & Personal
        gpt.generate_video_with_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'facebook.txt'),
            db_remote_path=db_remote_path,
            upload_func=fb_content_repo.schedule_fb_video_post
        )

        # Twitter 
        gpt.generate_video_with_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
            db_remote_path=db_remote_path,
            upload_func=twitter_content_repo.schedule_video_tweet
        )
        gpt.generate_text_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'tweetstorm.txt'),
            post_num=8,
            upload_func=twitter_content_repo.schedule_tweet,
            should_polish=True
        )

        #LinkedIn
        gpt.generate_text_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'linkedin.txt'),
            post_num=1,
            upload_func=linkedin_content_repo.schedule_post,
            should_polish=True
        )
   
        # Medium
        gpt.generate_text_prompt(
            prompt_source=os.path.join('src', 'input_prompts', 'blog.txt'),
            post_num=1,
            upload_func=medium_content_repo.schedule_medium_article
        )

        # Move file and additional cleanup
        dropbox_storage.move_file(db_remote_path, '/ContentUploaded/' + os.path.basename(db_remote_path))
        print('Finished and completed')
    