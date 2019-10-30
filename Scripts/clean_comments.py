import argparse
import os
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


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

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    for sub in subreddits:
        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}\Raw\{sub}.json', 'r') as f:
            comments = json.load(f)

        filtered_comments = []
        for comment in comments:
            sent = comment['comment']
            sent = keep_alphabetical(sent)

            word_tokens = word_tokenize(sent)
            filtered_sentence = [w for w in word_tokens if not w in stop_words]
            sent = ' '.join(filtered_sentence)

            word_tokens = word_tokenize(sent)
            tokens = nltk.pos_tag(word_tokens)
            final_words = ' '.join([lemmatizer.lemmatize(pair[0], get_wordnet_pos(pair[1])) for pair in tokens])

            filtered_comments.append(
                {'comment_id': comment['comment_id'], 'post_id': comment['post_id'], 'comment': final_words})

        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\Text\{cat}\Processed\{sub}.json', 'w') as f:
            json.dump(filtered_comments, f)


def keep_alphabetical(text):
    if text is None:
        return text
    cleaned = filter_url(text)
    cleaned = re.sub(r'\n', ' ', cleaned)
    cleaned = re.sub(r'[*]', '', cleaned)
    cleaned = re.sub(r'\[', '', cleaned)
    cleaned = re.sub(r'\]', '', cleaned)
    cleaned = re.sub(r'[(]', '', cleaned)
    cleaned = re.sub(r'[)]', '', cleaned)
    cleaned = re.sub(r'[/]*r/[a-zA-Z0-9_]+[/[a-zA-Z0-9_]*]*', '', cleaned)
    cleaned = re.sub(r'[#]+', '', cleaned)
    cleaned = re.sub(r'[.?!)]+', r' ', cleaned)
    cleaned = re.sub(r'/', ' ', cleaned)
    cleaned = re.sub(r'[,;=:<>]', '', cleaned)
    cleaned = re.sub(r'"', '', cleaned)
    cleaned = re.sub(r'[0-9]+', '', cleaned)
    cleaned = re.sub(r'(~)+', '', cleaned)
    cleaned = re.sub(r'[$%^+-@&]+', '', cleaned)

    return cleaned.lower()


def filter_url(text):
    return re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", '', text)


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


if __name__ == '__main__':
    main()