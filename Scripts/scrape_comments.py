import argparse
import configparser
import logging
import praw
import os
import json


def main():
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)  # logging info
    parser = argparse.ArgumentParser(description='Scrape comments from Reddit using PRAW, a registered Reddit account, '
                                                 'and a valid Reddit dev application.  Scraped comments will be stored '
                                                 'in .json format in appropriate folders, under the "Raw" section.')
    config = configparser.ConfigParser()  # reading configuration file (to get Reddit account and application details)

    parser.add_argument('c', metavar='CATEGORY', type=str, nargs='+', help='category')
    args = parser.parse_args()  # parse arguments

    categories = args.c  # get list of categories to scrape
    config.read(r'C:\Users\jonat\Desktop\Data Mining\Project\configuration.conf')  # read and parse configuration file

    for cat in categories:  # scrape subreddits in each category
        os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}')  # change to category's directory

        subreddits = []  # for storing list of subreddits

        with open(f'{cat}_list.txt', 'r') as f:  # read in list of subreddits from sub_list.txt
            for line in f:
                subreddits.append(line.replace('\n', ''))

        reddit = praw.Reddit(client_id=config['Reddit']['client_id'],
                             client_secret=config['Reddit']['client_secret'],
                             password=config['Reddit']['password'],
                             user_agent=config['Reddit']['user_agent'],
                             username=config['Reddit']['username'])  # create Reddit instance

        for sub_name in subreddits:  # scrape each subreddit
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
                json.dump(comments, f)  # dump scraped data in .json format


if __name__ == '__main__':
    main()

