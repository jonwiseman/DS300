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

    parser.add_argument('c', metavar='CATEGORY', type=str, help='category')
    args = parser.parse_args()

    cat = args.c
    config.read(r'C:\Users\jonat\Desktop\Data Mining\Project\configuration.conf')
    os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}')

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
        submissions = sub.top(limit=10)

        comments = []
        for submission in submissions:
            submission.comments.replace_more(limit=10)
            count = 0
            for top_level_comment in submission.comments:
                if count < 50:
                    comments.append({'comment_id': top_level_comment.id,
                                     'post_id': top_level_comment.submission.id,
                                     'comment': top_level_comment.body})
                    for second_level_comment in top_level_comment.replies:
                        comments.append({'comment_id': second_level_comment.id,
                                         'post_id': second_level_comment.submission.id,
                                         'comment': second_level_comment.body})
                    count += 1

        logging.info(f'{len(comments)} scraped from r/{sub_name}\n')
        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}\Raw\{sub}.json', 'w') as f:
            json.dump(comments, f)


if __name__ == '__main__':
    main()