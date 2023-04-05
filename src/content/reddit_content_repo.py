import appsecrets
import praw

#NOTE: THIS CLASS IS TO ONLY BE USED WITH PERSONAL BRAND BOT
#   these subreddits need to be joined and the right flairs added
subreddit_flairs = {
    "socialskills": "Self-Improvement",
    "AskMen": "Discussion",
    "OneY": "Discussion",
    "Manprovement": "Self-Improvement",
    "MaleSupportNetwork": "Support",
    "malefashionadvice": "Fashion",
    "MaleLivingSpace": "Lifestyle",
    "malegrooming": "Grooming",
    "Meditation": "Self-Improvement",
    "nofap": "Self-Improvement",
    "stopdrinking": "Self-Improvement",
    "productivity": "Self-Improvement",
    "Mindfulness": "Self-Improvement",
    "DecidingToBeBetter": "Self-Improvement",
    "GetMotivated": "Self-Improvement",
    "LifeProTips": "Tips",
    "LearnUselessTalents": "Hobby",
    "LearnProgramming": "Hobby",
    "LearnMusic": "Hobby",
    "LearnArt": "Hobby",
    "Photography": "Hobby",
    "Travel": "Lifestyle",
    "Cooking": "Hobby",
    "DIY": "Hobby",
    "woodworking": "Hobby",
    "homeimprovement": "Hobby",
    "Entrepreneur": "Business",
    "personalfinance": "Finance",
    "FinancialPlanning": "Finance",
    "Investing": "Finance",
    "StockMarket": "Finance",
    "RealEstate": "Finance",
    "fitness": "Fitness",
    "bodyweightfitness": "Fitness",
    "running": "Fitness",
    "yoga": "Fitness",
    "martialarts": "Fitness",
    "sports": "Sports",
    "basketball": "Sports",
    "football": "Sports",
    "soccer": "Sports",
    "tennis": "Sports",
    "golf": "Sports",
    "seduction": "Dating",
    "dating_advice": "Dating",
    "relationships": "Relationships",
    "sex": "Sexuality",
    "malelifestyle": "Lifestyle",
    "bropill": "Lifestyle",
    "Gaybros": "LGBTQ+",
    "LGBT": "LGBTQ+",
    "bisexual": "LGBTQ+",
    "gaymers": "LGBTQ+",
    "gayyoungold": "LGBTQ+",
    "gay": "LGBTQ+",
    "MeetNewPeopleHere": "Friendship",
    "MakeNewFriendsHere": "Friendship",
    "Needafriend": "Friendship",
    "FriendshipAdvice": "Friendship",
    "Music": "Music",
    "Movies": "Entertainment",
    "Books": "Entertainment",
    "Games": "Gaming",
    "PCMasterRace": "Gaming",
    "PS4": "Gaming",
    "XboxOne": "Gaming",
    "NintendoSwitch": "Gaming",
    "BoardGames": "Gaming",
    "CardGames": "Gaming",
    "Anime": "Entertainment",
    "manga": "Entertainment",
    "comicbooks": "Entertainment",
    "Art": "Art",
    "LearnArt": "Art",
    "writing": "Art",
    "screenwriting": "Art",
    "acting": "Art",
    "filmmakers": "Art",
    "filmmaking": "Art",
}


reddit = praw.Reddit(
    client_id=appsecrets.REDDIT_CLIENT_ID,
    client_secret=appsecrets.REDDIT_CLIENT_SECRET,
    username=appsecrets.REDDIT_USERNAME,
    password=appsecrets.REDDIT_PASSWORD,
    user_agent="AIContentMachine",
)

def get_flair_id( subreddit, flair_text ):
    # Get the list of available flair templates
    flair_templates =  list(subreddit.flair.link_templates.user_selectable())
    desired_template = next((template for template in flair_templates if template['flair_text'] == flair_text), None)

    if desired_template:
        # Get the flair ID for the desired template
        flair_id = desired_template['flair_template_id']
        return flair_id
    else:
        # Handle the case where the desired template is not found
        print(f"No flair template found with text '{flair_text}'")     

def post_to_subreddit( title, text, image_query ):
    for subreddit_key, flair_value in subreddit_flairs.items():
        subreddit = reddit.subreddit(subreddit_key)
        flair = get_flair_id(subreddit, flair_value)
        result = subreddit.submit(title=title, selftext=text, flair_id=flair)
        print(result.url)

