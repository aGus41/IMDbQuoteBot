import tweepy
import requests
import imdb
import time
import random
from bs4 import BeautifulSoup

consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'

access_token = 'access_token'
access_token_secret = 'access_token_secret'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
# wait_on_rate_limit enabled to ensure that the 300 tweets per hour per account limitation is not exceeded

FILE_NAME = 'last_id.txt'

ia = imdb.IMDb()


def thread_reply(parts, tweet_id, i=0):
    # Recursive method to create a tweet thread from each quote
    if i < len(parts) - 1:
        i += 1
        next_tweet = api.update_status(parts[i], tweet_id)
        thread_reply(parts, next_tweet.id, i)
    else:
        print('All tweets sent')


def tweet_parser(lines, movie_title, movie_year, url, username=''):
    tweet_length = 280
    whole_thread = username + ' ' + '\n'.join(lines)
    if len(whole_thread) < tweet_length:
        # The quote fits in one tweet
        parts = list()
        parts.append(whole_thread)
        parts.append(movie_title + ' (' + str(movie_year) + ') ' + '#MovieQuotes ' + url)
        return parts
    else:
        # Divide the Quote in tweets length. Store each tweet as a new element in the list 'parts'
        parts = [whole_thread[i:i + tweet_length] for i in range(0, len(whole_thread), tweet_length)]
        parts.append(movie_title + ' (' + str(movie_year) + ') ' + '#MovieQuotes ' + url)
        return parts


def imdb_lookup(movie_title_tosearch, number_of_quotes, is_it_random=False):
    try:
        movies = ia.search_movie(movie_title_tosearch)
        movie_id = movies[0].movieID
        movie_title = movies[0]['title']
        movie_year = movies[0]['year']
    except IndexError:
        # IMDbPY search tool returns 0 movies
        return 'No movies found', '', '', ''

    url = 'https://www.imdb.com/title/tt' + movie_id + '/quotes/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    quotes = soup.find_all('div', {'class': 'sodatext'})
    if len(quotes) == 0:
        if is_it_random is True:
            return None, None, None, None
        # IMDbPY search tool returns a valid movie but with no quotes in it
        return 'This movie has no quotes', url, movie_title, movie_year
    elif is_it_random is False:
        tweets = []
        if number_of_quotes > len(quotes):
            number_of_quotes = len(quotes)
        for i in range(number_of_quotes):
            character_lines = quotes[i].find_all('p')
            lines = []
            for line in character_lines:
                lines.append(line.text.replace('\n', ' '))
            tweets.append(lines)
        # Each element of 'lines' is a character line for a quote
        # Each element of 'tweets' is a list of character lines of a single quote
        return tweets, url, movie_title, movie_year
    else:
        tweets = []
        rnd = random.randrange(len(quotes) - 1)
        character_lines = quotes[rnd].find_all('p')
        # Selects a random quote (from a random movie)
        lines = []
        for line in character_lines:
            lines.append(line.text.replace('\n', ' '))
        tweets.append(lines)
        return tweets, url, movie_title, movie_year


def get_random_movie():
    # Return a random movie between IMDb top 250
    top250 = ia.get_top250_movies()
    rnd = random.randrange(249)
    # print(rnd)
    return top250[rnd]['title'] + ' ' + str(top250[rnd]['year'])
    # return 'Spotlight 2018'


def get_random_quote():
    tweets, url, movie_title, movie_year = imdb_lookup(get_random_movie(), 1, True)
    if tweets is None:
        pass
    else:
        try:
            for line in tweets:
                parts = tweet_parser(line, movie_title, movie_year, url)
                first_tweet = api.update_status(parts[0])
                thread_reply(parts, first_tweet.id)
        except tweepy.error.TweepError:
            get_random_quote()


counter = 0

get_random_quote()

