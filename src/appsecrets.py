from google.cloud import secretmanager

project_id = "ai-content-machine"

def access_secret(secret_id, version="1"):
    print(f"Accessing secret {secret_id}")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

OPEN_AI_API_KEY=access_secret("OPEN_AI_API_KEY")
DROPBOX_APP_ID=access_secret("DROPBOX_APP_ID")
DROPBOX_APP_SECRET=access_secret("DROPBOX_APP_SECRET")
DROPBOX_AUTH_CODE=access_secret("DROPBOX_AUTH_CODE")
TWITTER_API_KEY=access_secret("TWITTER_API_KEY")
TWITTER_API_SECRET=access_secret("TWITTER_API_SECRET")
TWITTER_API_BEARER=access_secret("TWITTER_API_BEARER")
TWITTER_API_AUTH_TOKEN=access_secret("TWITTER_API_AUTH_TOKEN", "2")
TWITTER_API_AUTH_SECRET=access_secret("TWITTER_API_AUTH_SECRET", "2")
UNSPLASH_ACCESS_KEY=access_secret("UNSPLASH_ACCESS_KEY")
MEDIUM_API_KEY=access_secret("MEDIUM_API_KEY")
META_APP_ID=access_secret("META_APP_ID")
META_APP_SECRET=access_secret("META_APP_SECRET")
FACEBOOK_GRAPH_API_PAGE_ID=access_secret("FACEBOOK_GRAPH_API_PAGE_ID")
INSTAGRAM_GRAPH_API_PAGE_ID=access_secret("INSTAGRAM_GRAPH_API_PAGE_ID")
REBRANDLY_API_KEY=access_secret("REBRANDLY_API_KEY")
FIREBASE_CONFIG=access_secret("FIREBASE_CONFIG", "2")
#this is our amohnacs@gmail.com google account
REDDIT_CLIENT_ID=access_secret("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET=access_secret("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME=access_secret("REDDIT_USERNAME")
REDDIT_PASSWORD=access_secret("REDDIT_PASSWORD")
