import sys
import os
import whisper
import warnings
warnings.filterwarnings("ignore")
import openai
import textwrap
import utility.utils as utils
import appsecrets as appsecrets

# This code retrieves the current directory path and appends the '../src' directory to the sys.path, allowing access to modules in that directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

openai.api_key = appsecrets.OPEN_AI_API_KEY  

'''GPT #

    Args:
        string: Prompt for GPT processing

    Returns:
        String of AI generated content
'''
def gpt_3(prompt):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=1.2,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        text = response['choices'][0]['text'].strip()
        return text
    except Exception as err:
        print(err)
        return ''
    

def mp3_to_transcript(mp3_file_path):
    print('Processing mp3 to transcript')
    sound = mp3_file_path
    model = whisper.load_model("medium")
    result = model.transcribe(sound, fp16=False, language = 'en')

    yttrans = (result['text'])
    result_path = mp3_file_path.replace('.mp3', '_transcript.txt')
    utils.save_file(result_path, yttrans)
    print(f'saved mp3 transcript: {yttrans}')
    return result_path

def transcript_to_summary(transcript_file_path):
    print('Processing transcript to summary')
    alltext = utils.open_file(transcript_file_path)
    chunks = textwrap.wrap(alltext, 2500)
    result = list()
    count = 0
    for chunk in chunks:
        print("🚀 ~ file: gpt.py:56 ~ chunk:", chunk)
        count = count + 1
        file_path_input = os.path.join("src", "input_prompts", "summary.txt")
        prompt = utils.open_file(file_path_input).replace('<<SUMMARY>>', chunk)
        print("🚀 ~ file: gpt.py:58 ~ prompt:", prompt)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt_3(prompt)
        print('\n\n\n', count, 'out of', len(chunks), 'Compressions', ' : ', summary)
        result.append(summary)
    file_path_output = os.path.join("src", "outputs", "summary_output.txt")    
    utils.save_file(file_path_output, '\n\n'.join(result))
    return file_path_output

def gpt_generate_summary( chunk ):
    file_path_input = os.path.join("src", "input_prompts", "summary.txt")
    prompt = utils.open_file(file_path_input).replace('<<SUMMARY>>', chunk)
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    summary = gpt_3(prompt)
    file_path_output = os.path.join("src", "outputs", "summary_output.txt")    
    utils.save_file(file_path_output, summary)

def get_gpt_generated_text( prompt_source ):
    # get the first draft of the generated text
    feedin_source_file = os.path.join("src", "outputs", "summary_output.txt")
    feed_source = utils.open_file(feedin_source_file)
    applied_prompt = utils.open_file(prompt_source).replace('<<FEED>>', feed_source)
    return gpt_3(applied_prompt)

def generate_video_with_prompt( 
        prompt_source, 
        db_remote_path, 
        upload_func
    ):
    """
    Convert a single file of language to another using chat GPT as a video
        
        Args:
            feedin_source (str): The path to the file.
            prompt_source (str): The path for the GPT prompt.
            type (str): simple categorization to help with naming
            dropbox_file_path (str): The path to the file in the Dropbox app directory.

        Example:
            dropbox_upload_file('.', 'test.csv', '/stuff/test.csv')

        Returns: 
            Nothing
    """
    print(f'Video prompt {prompt_source}')
    gpt_text = get_gpt_generated_text(prompt_source)

    upload_func(gpt_text, db_remote_path)

def generate_text_prompt( 
        prompt_source, 
        post_num, 
        upload_func
    ):
    
    for num in range(post_num):
        print(f'Processing #{num + 1} of {prompt_source}')
        gpt_text = get_gpt_generated_text(prompt_source)

        upload_func(gpt_text)

def prompt_to_string_from_file( prompt_source_file, feedin_source_file ):
    print("🚀 ~ file: gpt.py:129 ~ prompt_to_string_from_file:", prompt_source_file, feedin_source_file)
    feed_source = utils.open_file(feedin_source_file)
    appliedprompt = utils.open_file(prompt_source_file).replace('<<FEED>>', feed_source)
    finaltext = gpt_3(appliedprompt)
    return finaltext

def prompt_to_string( prompt_source_file, feedin_source ):
    print("🚀 ~ file: gpt.py:136 ~ prompt_to_string:", prompt_source_file, feedin_source)
    appliedprompt = utils.open_file(prompt_source_file).replace('<<FEED>>', feedin_source)
    finaltext = gpt_3(appliedprompt)
    return finaltext

def link_prompt_to_string( prompt_source_file, feedin_title, feedin_link ):
    print("🚀 ~ file: gpt.py:142 ~ link_prompt_to_string:", prompt_source_file, feedin_title, feedin_link)
    appliedprompt = utils.open_file(prompt_source_file).replace('<<TITLE>>', feedin_title).replace('<<LINK>>', feedin_link)
    finaltext = gpt_3(appliedprompt)
    return finaltext
