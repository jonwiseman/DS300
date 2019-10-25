import argparse
import praw
import os
import spacy
import json
import re
import pickle
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('c', metavar='CATEGORY', type=str, help='category')
    args = parser.parse_args()

    cat = args.c

    reddit = praw.Reddit(client_id='eQt4_moPBnQ8xg',
                         client_secret='t8WuNRzCPPBUkBJbyV10MO3nWr0',
                         password='AnimeTiddies5',
                         user_agent='Windows:com.example.myredditapp:v1.0.0 (by /u/dig_bick69_420)',
                         username='dig_bick69_420')

    nlp = spacy.load("en_core_web_sm")
    lookups = Lookups()
    lookups.add_table("lemma_rules", {"noun": [["s", ""]]})
    lemmatizer = Lemmatizer(lookups)

    os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}')

    subreddits = []

    with open(f'{cat}_list.txt', 'r') as f:
        for line in f:
            subreddits.append(line.replace('\n', ''))

    for sub_name in subreddits:
        sub = reddit.subreddit(sub_name)
        submissions = sub.top(limit=10)
        comments = []

        for submission in submissions:
            submission.comments.replace_more(limit=0)
            count = 0
            for top_level_comment in submission.comments:
                if count < 30:
                    comments.append(top_level_comment.body)
                    for second_level_comment in top_level_comment.replies:
                        comments.append(second_level_comment.body)
                    count += 1

        new_word_list = []

        for comment in comments:
            cleaned_comment = clean_text(comment)
            doc = nlp(cleaned_comment)
            words = []
            for word in doc:
                if not word.is_stop and not word.is_punct:
                    words.append(lemmatizer(word.text, word.pos_)[0])

            new_word_list.extend(words)

        pickle.dump(new_word_list,
                    open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}\{sub.display_name}.pickle',
                         'wb'))


def clean_text(text):
    if text is None:
        return text
    cleaned = re.sub(r'\s\s+', ' ', text)
    cleaned = re.sub(r'\n', '', cleaned)
    cleaned = re.sub(r'\s([,.?!;)])', r'\1', cleaned)
    cleaned = re.sub(r'No. (\d)', r'number \1', cleaned)

    return cleaned.lower()


if __name__ == '__main__':
    main()