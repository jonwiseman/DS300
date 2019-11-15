import argparse
import logging
import os
import glob
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def main():
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser('Generate all user-specified data visualizations for cleaned comments')
    parser.add_argument('-c', metavar='CATEGORY', required=True, type=str, nargs='+', help='category')
    parser.add_argument('-s', metavar='STEM_TYPE', required=True, type=str,
                        nargs='+', help='stemming type')
    args = parser.parse_args()  # parse arguments

    categories = args.c  # categories for visualizing
    stems = args.s  # stemming types to visualize

    if 'all' in stems:
        stems = ['lancaster', 'lemma', 'porter']

    n_stems = int('lancaster' in stems) + int('lemma' in stems) + int('porter' in stems)
    if n_stems == 0:
        logging.error('Invalid stem choice')
        raise InputError

    if 'all' in categories:
        categories = ['sports', 'reading', 'politics_news', 'music', 'gaming', 'art', 'tech', 'science']

    logging.info('Generating wordclouds...')
    documents = get_document_array('lemma', categories)
    for cat in categories:  # generate wordclouds first
        subs = documents[documents[:, 1] == cat]  # get all subs in current category
        fig, ax = plt.subplots(ncols=len(subs), figsize=[20, 20])  # create subplot to hold all wordclouds in category

        for i, axis in enumerate(ax):  # plot wordclouds
            wordcloud = WordCloud(max_words=10, background_color='white', width=1000, height=500,
                                  colormap='coolwarm').generate(subs[i][0])
            axis.imshow(wordcloud)
            axis.axis("off")
            axis.set_title(f'r/{subs[i][3]}')  # display subreddit title
        logging.info(fr'Generated wordcloud for {cat}')
        plt.savefig(fr'C:\Users\jonat\Desktop\Data Mining\Project\Images\word_clouds\{cat}.png')

    logging.info('Generating vector plots...')  # Generate plots for document vectorizations
    for stem in stems:  # use each specified stemming type
        for end in range(1, 4):  # specifies n-gram ranges
            documents = get_document_array(stem, categories)  # tf-idf vectorize all subs
            tfidf_vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, end))
            X = tfidf_vectorizer.fit_transform(documents[:, 0])
            svd = TruncatedSVD()  # reduce to two dimensions for plotting

            X = svd.fit_transform(X)  # apply singular value decomposition

            colors = {'sports': ['red', 0], 'reading': ['orange', 0], 'politics_news': ['yellow', 0],
                      'music': ['green', 0], 'gaming': ['blue', 0], 'art': ['indigo', 0], 'tech': ['violet', 0],
                      'science': ['black', 0]}  # for making sure that there is only one label for each category

            fig = plt.figure(figsize=[15, 8])
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

            for i, sub in enumerate(X):
                ax.plot(sub[0], sub[1], color=colors[documents[i][1]][0], marker='o',
                        label=get_label(i, colors, documents))

            ax.legend()
            ax.set_title(f'TF-IDF Vectorization up to {end}-grams')
            plt.savefig(fr'C:\Users\jonat\Desktop\Data Mining\Project\Images\idf\{stem}\{end}_gram.png')
            plt.close(fig)  # close figure object to save memory
            logging.info(f'Generated tf-idf vector plot for {stem} with up to {end}-grams')
        for end in range(1, 4):  # generate plots for count vectorizer
            documents = get_document_array(stem, categories)
            count_vectorizer = CountVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, end))
            X = count_vectorizer.fit_transform(documents[:, 0])
            svd = TruncatedSVD()

            X = svd.fit_transform(X)

            colors = {'sports': ['red', 0], 'reading': ['orange', 0], 'politics_news': ['yellow', 0],
                      'music': ['green', 0], 'gaming': ['blue', 0], 'art': ['indigo', 0], 'tech': ['violet', 0],
                      'science': ['black', 0]}

            fig = plt.figure(figsize=[15, 8])
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

            for i, sub in enumerate(X):
                ax.plot(sub[0], sub[1], color=colors[documents[i][1]][0], marker='o',
                        label=get_label(i, colors, documents))

            ax.legend()
            ax.set_title(f'Count Vectorization with up to {end}-grams')
            plt.savefig(fr'C:\Users\jonat\Desktop\Data Mining\Project\Images\count\{stem}\{end}_gram.png')
            plt.close(fig)
            logging.info(f'Generated count vector plot for {stem} with up to {end}-grams')


def get_label(i, colors, documents):
    """
    I was having trouble getting only one label to show up on the legend for each category, so this method allows that.
    :param i: current document
    :param colors: color specification dictionary
    :param documents: document array
    :return: label to be applied to point, or no label if that category is already represented
    """
    if colors[documents[i][1]][1] == 0:
        colors[documents[i][1]][1] += 1
        return documents[i][1]
    else:
        return ""


def get_document_array(stem, categories):
    """
    Create a document array for a given stemming type and list of categories
    :param stem: stemming type (lemma, lancaster, or porter)
    :param categories: list of categories that will be vectorized
    :return: document array for vectorizing
    """
    documents = []
    for cat in categories:
        os.chdir(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Processed\{stem}')
        files = glob.glob('*.json')
        for file in files:
            with open(fr'C:\Users\jonat\Desktop\Data Mining\Project\Data\{cat}\Processed\{stem}\{file}', 'r') as f:
                comments = json.load(f)
            documents.append((' '.join([comment['comment'] for comment in comments]), cat, cat, file.split('.json')[0]))

    documents = np.array(documents)
    encoder = LabelEncoder()
    documents[:, 2] = encoder.fit_transform(documents[:, 2])
    return documents


class InputError(Exception):
    """Invalid input from user"""


if __name__ == '__main__':
    main()
