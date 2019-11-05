import argparse
import configparser
import logging
import praw
import os
import json


def main():
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()

    parser.add_argument('c', metavar='CATEGORY', type=str, nargs='+', help='category')
    args = parser.parse_args()

    categories = args.c
    config.read(r'C:\Users\jonat\Desktop\Data Mining\Project\configuration.conf')

    for cat in categories:
        os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}')

        subreddits = []

        with open(f'{cat}_list.txt', 'r') as f:
            for line in f:
                subreddits.append(line.replace('\n', ''))

        reddit = praw.Reddit(client_id=config['Reddit']['client_id'],
                             client_secret=config['Reddit']['client_secret'],
                             password=config['Reddit']['password'],
                             user_agent=config['Reddit']['user_agent'],
                             username=config['Reddit']['username'])

        for sub_name in subreddits:
            logging.info(f'Scraping comments for r/{sub_name}')
            sub = reddit.subreddit(sub_name)
            comments = []
            for submission in sub.top(limit=100):
                for top_level_comment in submission.comments:
                    if type(top_level_comment) is praw.models.reddit.comment.Comment:
                        comments.append({'comment_id': top_level_comment.id,
                                         'post_id': top_level_comment.submission.id,
                                         'comment': top_level_comment.body})

            logging.info(f'{len(comments)} scraped from r/{sub_name}\n')
            with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Raw\{sub}.json', 'w') as f:
                json.dump(comments, f)


if __name__ == '__main__':
    main()

