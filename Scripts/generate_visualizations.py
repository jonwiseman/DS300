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
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', metavar='CATEGORY', required=True, type=str, nargs='+', help='category')
    parser.add_argument('-s', metavar='STEM_TYPE', required=True, type=str,
                        nargs='+', help='stemming type')
    args = parser.parse_args()

    categories = args.c
    stems = args.s

    if 'all' in stems:
        stems = ['lancaster', 'lemma', 'porter']

    n_stems = int('lancaster' in stems) + int('lemma' in stems) + int('porter' in stems)
    if n_stems == 0:
        logging.error('Invalid stem choice')
        return

    if 'all' in categories:
        categories = ['sports', 'reading', 'politics_news', 'music', 'gaming', 'art', 'tech', 'science']

    logging.info('Generating wordclouds...')
    documents = get_document_array('lemma', categories)
    for cat in categories:
        subs = documents[documents[:, 1] == cat]
        fig, ax = plt.subplots(ncols=len(subs), figsize=[20, 20])

        for i, axis in enumerate(ax):
            wordcloud = WordCloud(max_words=10, background_color='white', width=1000, height=500,
                                  colormap='coolwarm').generate(subs[i][0])
            axis.imshow(wordcloud)
            axis.axis("off")
            axis.set_title(f'r/{subs[i][3]}')
        logging.info(fr'Generated wordcloud for {cat}')
        plt.savefig(fr'C:\Users\jonat\Desktop\Data Mining\Project\Images\word_clouds\{cat}.png')

    logging.info('Generating vector plots...')
    for stem in stems:
        for end in range(1, 4):
            documents = get_document_array(stem, categories)
            tfidf_vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, end))
            X = tfidf_vectorizer.fit_transform(documents[:, 0])
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
            ax.set_title(f'TF-IDF Vectorization up to {end}-grams')
            plt.savefig(fr'C:\Users\jonat\Desktop\Data Mining\Project\Images\idf\{stem}\{end}_gram.png')
            plt.close(fig)
            logging.info(f'Generated tf-idf vector plot for {stem} with up to {end}-grams')
        for end in range(1, 4):
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
    if colors[documents[i][1]][1] == 0:
        colors[documents[i][1]][1] += 1
        return documents[i][1]
    else:
        return ""


def get_document_array(stem, categories):
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


if __name__ == '__main__':
    main()
