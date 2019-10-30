import argparse
import praw
import os
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('c', metavar='CATEGORY', type=str, help='category')
    args = parser.parse_args()

    cat = args.c
    os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}')

    subreddits = []

    with open(f'{cat}_list.txt', 'r') as f:
        for line in f:
            subreddits.append(line.replace('\n', ''))

    reddit = praw.Reddit(client_id='eQt4_moPBnQ8xg',
                         client_secret='t8WuNRzCPPBUkBJbyV10MO3nWr0',
                         password='AnimeTiddies5',
                         user_agent='Windows:com.example.myredditapp:v1.0.0 (by /u/dig_bick69_420)',
                         username='dig_bick69_420')

    for sub_name in subreddits:
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

        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}\Raw\{sub}.json', 'w') as f:
            json.dump(comments, f)

if __name__ == '__main__':
    main()