import sys
sys.path.append("../src")

import replicate
import appsecrets as appsecrets
import requests
import json
from storage.firebase_storage import PostingPlatform

# "raw": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d",
# "full": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg",
# "regular": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg&w=1080&fit=max",
# "small": "https://images.unsplash.com/photo-1417325384643-aac51acc9e5d?q=75&fm=jpg&w=400&fit=max",
# "thumb": "https

def get_unsplash_image_url( search_query, platform, orientation = 'portrait' ):
    if(platform == PostingPlatform.FACEBOOK):
        resolution_key='regular'
    elif(platform == PostingPlatform.INSTAGRAM):
        resolution_key='regular'
    elif(platform == PostingPlatform.TWITTER):
        resolution_key='regular'
    elif(platform == PostingPlatform.SHOPIFY):
        resolution_key='regular'    
    elif(platform == PostingPlatform.YOUTUBE):
        resolution_key='full'
    else:
        resolution_key='regular'        

    url = 'https://api.unsplash.com/photos/random'
    params = {
        'query': search_query,
        'orientation': orientation
    }
    headers = {
        'Accept-Version': "v1",
        'Authorization': 'Client-ID ' + appsecrets.UNSPLASH_ACCESS_KEY
    }
    response = requests.get( 
        url = url, 
        params = params,
        headers = headers
    )
    try:
        json_content = json.loads( response.content )
        if (json_content['urls'] is not None):
            result_url=json_content['urls'][resolution_key]
            return result_url
        else:
            return ''
    except:
        print(f'error with image {response}')
        return ''

def get_ai_image(visual_prompt, width = 512, height = 1024):
    api = replicate.Client(appsecrets.REPLICATE_TOKEN)
    model = api.models.get("tstramer/midjourney-diffusion")
    version = model.versions.get("436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b")

#     # https://replicate.com/tstramer/midjourney-diffusion/versions/436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b#input
    inputs = {
#         # Input prompt
        'prompt': visual_prompt,

#         # Specify things to not see in the output  
        'negative_prompt': 'people person man lady hand hands she he them woman face faces',

#         # Width of output image. Maximum size is 1024x768 or 768x1024 because # of memory limits
        'width': width,

#         # Height of output image. Maximum size is 1024x768 or 768x1024 because of memory limits
        'height': height,

#         # Prompt strength when using init image. 1.0 corresponds to full destruction of information in init image
        'prompt_strength': 0.8,

#         # Number of images to output. # Range: 1 to 4
        'num_outputs': 1,

#         # Number of denoising steps # Range: 1 to 500
        'num_inference_steps': 50,

#         # Scale for classifier-free guidance # Range: 1 to 20
        'guidance_scale': 7.5,

#         # Choose a scheduler.
        'scheduler': "DPMSolverMultistep",

#         # Random seed. Leave blank to randomize the seed
#         # 'seed': ...,
    }

#     # https://replicate.com/tstramer/midjourney-diffusion/versions/436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b#output-schema
    try:
        output = version.predict(**inputs)
        print(output[0])
        return output[0]
    except Exception as e:
        print(f'Image processing failed: {e}')
        return 'https://replicate.delivery/pbxt/YkWafGlPx70qIylnrCQvnNCPfseNNMHru9UWmVrQzc6Lw55gA/out-0.png'    