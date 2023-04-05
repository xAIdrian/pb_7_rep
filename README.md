# AI Content Machine 
A script to turn one YouTube video into content. Uploads automatically.

![57f43290c988cd447f8e5a5c3e6a09ad](https://user-images.githubusercontent.com/7444521/222048539-cd7220fe-ec96-45cc-985a-d4027c35b203.jpg)

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
$ python -m venv venv
$ & c:/Users/Infinix/Developer/seven_contents_by_ai/venv/Scripts/Activate.ps1
# only run first time
$ pip install -r requirements.txt
$ cp .env.example .env
```

Run this every time we work with our project:
'. venv\scripts\activate  '

Use this to start flask and set the environment variable
```
set FLASK_APP=hello.py
$env:FLASK_APP = "hello.py"
flask run
```

### Here are the commands we're using to get into a gcloud instance:
```
docker build --tag seven_contents_by_ai_docker_flamingo . 
docker tag seven_contents_by_ai_docker_flamingo gcr.io/ai-content-machine/seven_contents_by_ai_docker_flamingo
docker run gcr.io/ai-content-machine/seven_contents_by_ai_docker_flamingo 
docker push gcr.io/ai-content-machine/seven_contents_by_ai_docker_flamingo
```

### Execute on a schedule with Google Cloud Run Scheduler
instruction https://cloud.google.com/run/docs/execute/jobs-on-schedule
