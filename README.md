![57f43290c988cd447f8e5a5c3e6a09ad](https://user-images.githubusercontent.com/7444521/222048539-cd7220fe-ec96-45cc-985a-d4027c35b203.jpg)
# AI Content Machine

AI Content Machine is a Python application that automates the process of generating and scheduling content for various social media platforms. The application uses Google Cloud Run Scheduler to check for uploaded videos in Dropbox, generates a transcript using the Whisper API, and uses OpenAI to generate content for LinkedIn, Facebook, Instagram, Medium, Twitter, and YouTube. The content is then scheduled using Firebase Realtime Database.

## Dependencies

The application uses the following libraries and APIs:

- Google Cloud Run Scheduler
- Dropbox API
- Whisper API
- OpenAI API
- Firebase Realtime Database
- Python libraries: os, sys

## Modules

The application is divided into several modules:

- `ai.gpt`: Handles the generation of content using OpenAI.
- `storage.dropbox_storage`: Handles interactions with Dropbox.
- `content.*_content_repo`: Each of these modules handles the generation and scheduling of content for a specific platform (Instagram, Facebook, Twitter, YouTube, LinkedIn, Medium).
- `media.video_converter`: Handles the conversion of video files to different formats.

## Running the Application

To run the application after cloning the repository, follow these steps:

1. Navigate to the root directory of the project.
2. Run the main Python script with the command `python main.py`.



|           Dependencies               |         Install Lib:                         |
| :----------------------------------------- | :------------------------------ |
| Remember OpenAI API Key                                      |  pip install git+https://github.com/openai/whisper.git                               |
|  Run the script                             |  pip install numpy                                 |
| 1. Insert a YouTube URL in line 66                                    |  pip install openai                                |
| 2. Set your PATH folder in line 70                                    |  pip install Youtube_dl                                  |
| 3. Run the script                      |     pip install textwrap                               |

Install FFmpeg - Links in YouTube Tutorial: https://youtu.be/o-jQHQzjEjo 
Discord if you have any Questions 

### My Personal Notes
install everything with pip3

[If our linked in token is no good then follow the instructions here to get a new one from the browser window](https://www.jcchouinard.com/linkedin-api/)

Our Meta Graph tokens expire very quickly, after one day.  You will need to go back [here](https://developers.facebook.com/tools/explorer/) and get your access tokens:
- access token for specific pages/IG
- access token for user

Risky Dependencies:
https://github.com/nhorvath/Pyrebase4/blob/master/pyrebase/pyrebase.py

# Instructions for quickstart
https://github.com/openai/openai-quickstart-python
```bash
# run with each new terminal
$ python -m venv venv && source venv/bin/activate
# only run first time
$ pip install -r requirements.txt
$ cp .env.example .env
```

Run this every time we work with our project:
`. venv\scripts\activate`

### Here are the commands we're using to get into a gcloud instance:
```
gcloud init
gcloud run deploy
```
for mac:
```
https://cloud.google.com/build/docs/build-push-docker-image
```
### Execute on a schedule with Google Cloud Run Scheduler
instruction https://cloud.google.com/run/docs/execute/jobs-on-schedule
