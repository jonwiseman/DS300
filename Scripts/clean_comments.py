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
    parser = argparse.ArgumentParser(description='Apply text processing to scraped comment dataset.  All stop words are'
                                                 'removed, and text is either stemmed or lemmatized as specified by'
                                                 'the user.')
    parser.add_argument('-c', metavar='CATEGORY', required=True, type=str, nargs='+', help='category')
    parser.add_argument('-s', metavar='STEM_TYPE', required=True, type=str,
                        nargs='+', help='stemming type')  # user can specify stemming type (lemma is most useful)
    args = parser.parse_args()

    categories = args.c
    stems = args.s

    if 'all' in stems:  # if user wants to use each stemming method (useful when a new category has been scrubbed)
        stems = ['lancaster', 'lemma', 'porter']

    n_stems = int('lancaster' in stems) + int('lemma' in stems) + int('porter' in stems)  # number of stems specified
    if n_stems == 0:  # Error: no stems specified
        logging.error('Invalid stem choice')
        raise InputError

    for cat in categories:  # clean comments for each sub in each category
        os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}')

        subreddits = []  # get list of subreddits

        with open(f'{cat}_list.txt', 'r') as f:
            for line in f:
                subreddits.append(line.replace('\n', ''))

        stop_words = set(stopwords.words('english'))  # get list of stopwords (using NLTK)
        lemmatizer = WordNetLemmatizer()  # create wordnet lemmatizer
        porter = PorterStemmer()  # create stemming objects
        lancaster = LancasterStemmer()
        for stem in stems:  # apply each type of stemming to comments
            for sub in subreddits:
                logging.info(f'Cleaning comments for r/{sub} using {stem} stemming')
                with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Raw\{sub}.json', 'r') as f:
                    comments = json.load(f)

                filtered_comments = []  # list of processed comments for .json dump
                for comment in comments:
                    sent = comment['comment']  # get the comment data
                    sent = keep_alphabetical(sent)  # remove excess characters (see function definition)

                    word_tokens = word_tokenize(sent)  # tokenize into words
                    filtered_sentence = [w for w in word_tokens if w not in stop_words]  # remove stop words
                    sent = ' '.join(filtered_sentence)  # join back into a single string

                    word_tokens = word_tokenize(sent)  # word tokenize the new, filtered comment
                    tokens = nltk.pos_tag(word_tokens)  # tokenize into parts of speech
                    if stem == 'lemma':  # lemmatize
                        final_words = remove_stubs(' '.join([lemmatizer.lemmatize(pair[0], get_wordnet_pos(pair[1]))
                                                             for pair in tokens]))  # remove word stubs
                    elif stem == 'porter':  # porter stemmer
                        final_words = remove_stubs(' '.join([porter.stem(word) for word in word_tokens]))
                    else:  # lancaster stemmer
                        final_words = remove_stubs(' '.join([lancaster.stem(word) for word in word_tokens]))

                    filtered_comments.append(
                        {'comment_id': comment['comment_id'], 'post_id': comment['post_id'], 'comment': final_words})

                with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Processed\{stem}\{sub}.json', 'w') \
                        as f:
                    json.dump(filtered_comments, f)  # dump new .json file in appropriate folder


def keep_alphabetical(text):
    """
    Remove characters that have no value in document clustering.  This includes removing URLs, removing subreddit and
    Reddit user links, punctuation, numbers, emojis, and any other extraneous characters.
    :param text: a Reddit comment (string)
    :return: a cleaned Reddit comment (string)
    """
    if text is None:  # no text was given
        return text
    cleaned = filter_url(text)  # remove URLs
    cleaned = re.sub(r'\n', ' ', cleaned)  # remove newline characters
    cleaned = re.sub(r'[*]', '', cleaned)  # remove asterisks
    cleaned = re.sub(r'\[', '', cleaned)  # remove left brackets
    cleaned = re.sub(r'\]', '', cleaned)  # remove right brackets
    cleaned = re.sub(r'[(]', '', cleaned)  # remove left parentheses
    cleaned = re.sub(r'[)]', '', cleaned)  # remove right parentheses
    cleaned = re.sub(r'[/]*r/[a-zA-Z0-9_]+[/[a-zA-Z0-9_]*]*', '', cleaned)  # remove links to subreddits
    cleaned = re.sub(r'[#]+', '', cleaned)  # remove hashtags
    cleaned = re.sub(r'[.?!)]+', r' ', cleaned)  # remove punctiation
    cleaned = re.sub(r'/', ' ', cleaned)  # remove slashes
    cleaned = re.sub(r'[,;=:<>]', '', cleaned)  # remove other punctiation and miscellaneous characters
    cleaned = re.sub(r'"', '', cleaned)  # remove quotation marks
    cleaned = re.sub(r'[0-9]+', '', cleaned)  # remove numbers
    cleaned = re.sub(r'(~)+', '', cleaned)  # remove tildes
    cleaned = re.sub(r'[$%^+-@&_¯]+', '', cleaned)  # remove other miscellaneous characters
    cleaned = re.sub(r'\\', '', cleaned)  # remove back slashes
    cleaned = remove_emoji(cleaned)  # remove emojis

    return cleaned.lower()  # convert to lowercase and return


def filter_url(text):
    """
    Remove URLs from a given string
    :param text: string of text
    :return: string of text without URLs
    """
    return re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", '', text)


def get_wordnet_pos(treebank_tag):
    """
    Get parts of speech from wordnet.  Source: https://stackoverflow.com/a/15590384
    :param treebank_tag: tag assigned by tokenizer
    :return: part of speech corresponding to tokenizer's tag
    """
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
    """
    Remove word stubs from a lemmatized document.  Word stems include dangling apostrophes and apostrophe suffixes that
    are not actual words.
    :param document: cleaned and filtered document that has been lemmatized
    :return: a document without word stubs
    """
    word_tokens = word_tokenize(document)

    no_stubs = []
    for word in word_tokens:
        if r"'" not in word:  # grab those words that have apostrophes
            no_stubs.append(word)

    return ' '.join(no_stubs)


def remove_emoji(string):
    """
    Remove emojis from a string.  Source: https://stackoverflow.com/a/49146722.
    :param string: text string
    :return: text string without emojis
    """
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


class InputError(Exception):
    """Invalid input from user"""


if __name__ == '__main__':
    main()
