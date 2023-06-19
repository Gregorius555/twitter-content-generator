import tweepy
import feedparser
import openai
import pickle

# Twitter API Authentication
consumer_key = 'your_consumer_key_here'
consumer_secret = 'your_consumer_secret_here'
access_token = 'your_access_token_here'
access_token_secret = 'your_access_token_secret_here'

twitter_client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# OpenAI API Authentication
openai.api_key = 'your_openai_api_key_here'

# The Twitter users you want to paraphrase
users = ['user 1',
         'user 2',
         'user 3']

rss_urls = [f'https://nitter.net/{user}/rss' for user in users]

def save_parsed_tweets(parsed_tweets):
    with open('parsed_tweets.pkl', 'wb') as f:
        pickle.dump(parsed_tweets, f)

def load_parsed_tweets():
    try:
        with open('parsed_tweets.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {user: None for user in users}

# Load the previously parsed tweets
parsed_tweets = load_parsed_tweets()

def paraphrase(text):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=f"{text}\n\nParaphrase as a tweet and include source:",
      temperature=1,
      max_tokens=80
    )

    return response.choices[0].text.strip()

for user, rss_url in zip(users, rss_urls):
    # Fetch RSS feed
    feed = feedparser.parse(rss_url)

    # Check if there's a new tweet
    if feed.entries:
        newest_tweet = feed.entries[0]
        tweet_id = newest_tweet.id

        # If this is the first tweet we're fetching or there's a different tweet
        if user not in parsed_tweets:
            parsed_tweets[user] = None

        if parsed_tweets[user] is None or tweet_id != parsed_tweets[user]:
            parsed_tweets[user] = tweet_id

            # Extract original tweet and handle case where ':' doesn't exist in the tweet
            split_tweet = newest_tweet.title.split(': ', 1)
            original_tweet = split_tweet[1] if len(split_tweet) > 1 else split_tweet[0]

            paraphrased = paraphrase(original_tweet)

            # Post paraphrased tweet to Twitter
            try:
                response = twitter_client.create_tweet(
                    text=paraphrased
                )
                print(f"https://twitter.com/user/status/{response.data['id']}")
            except Exception as e:
                print(f"Error: {str(e)}")

# Save the parsed tweets
save_parsed_tweets(parsed_tweets)
