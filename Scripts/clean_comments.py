import argparse
import logging
import os
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer


def main():
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('c', metavar='CATEGORY', type=str, help='category')
    parser.add_argument('s', metavar='STEM_TYPE', type=str,
                        choices=['lemma', 'porter', 'lancaster'], help='stemming type', )
    args = parser.parse_args()

    cat = args.c
    stem = args.s
    os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}')

    subreddits = []

    with open(f'{cat}_list.txt', 'r') as f:
        for line in f:
            subreddits.append(line.replace('\n', ''))

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    porter = PorterStemmer()
    lancaster = LancasterStemmer()

    for sub in subreddits:
        logging.info(f'Cleaning comments for r/{sub}')
        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Raw\{sub}.json', 'r') as f:
            comments = json.load(f)

        filtered_comments = []
        for comment in comments:
            sent = comment['comment']
            sent = keep_alphabetical(sent)

            word_tokens = word_tokenize(sent)
            filtered_sentence = [w for w in word_tokens if w not in stop_words]
            sent = ' '.join(filtered_sentence)

            word_tokens = word_tokenize(sent)
            tokens = nltk.pos_tag(word_tokens)
            if stem == 'lemma':
                final_words = remove_stubs(' '.join([lemmatizer.lemmatize(pair[0], get_wordnet_pos(pair[1]))
                                                     for pair in tokens]))
            elif stem == 'porter':
                final_words = remove_stubs(' '.join([porter.stem(word) for word in word_tokens]))
            else:
                final_words = remove_stubs(' '.join([lancaster.stem(word) for word in word_tokens]))

            filtered_comments.append(
                {'comment_id': comment['comment_id'], 'post_id': comment['post_id'], 'comment': final_words})

        with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Processed\{stem}\{sub}.json', 'w') as f:
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
    cleaned = re.sub(r'[$%^+-@&_¯]+', '', cleaned)
    cleaned = re.sub(r'\\', '', cleaned)
    cleaned = remove_emoji(cleaned)

    return cleaned.lower()


def filter_url(text):
    return re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", '', text)


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


def remove_stubs(document):
    word_tokens = word_tokenize(document)

    no_stubs = []
    for word in word_tokens:
        if r"'" not in word:
            no_stubs.append(word)

    return ' '.join(no_stubs)


def remove_emoji(string):
    ''' Source: https://stackoverflow.com/a/49146722 '''
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


if __name__ == '__main__':
    main()