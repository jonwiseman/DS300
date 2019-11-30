This repository contains files related to the final project for DS300: Data Mining.

## Goal  
This project aims to utilize clustering techniques on Reddit comment data to produce subreddit and post recommendations.

## Methodology  
Reddit comments from posts from 37 subreddits spanning 8 "categories" that were assigned by hand to establish ground-truth for clustering.
Comment data was scraped for 37 subreddits spanning 8 hand-labeled categories (art, gaming, music, politics_news, reading, science, sports, and tech).  The top first- and second-level comments for the top 30 all-time posts from each subreddit were collected.  Text preprocessing in the form of removing non-alphabetic characters and URLs, stop word removal, and lemmatization/stemming were performed to clean the text dataset.  Comment data is stored in .json format, with the raw and processed text data available for each scraped subreddit in the "Data" folder.

Clustering models (including K-Means, Agglomerative Hierarchical, DBSCAN, OPTICS, Affinity Propagation, and Spectral Clustering) are then applied on both TF-IDF vectorized documents reducing using SVD and document embeddings producing using gensim's implementation of the Doc2Vec algorithm.  You can explore the results in the "Subreddit Clustering" and "Post Clustering" notebooks in the "Notebooks" folder.  The diagram below shows the overall project organization:

![Project organization](https://github.com/jonwiseman/DS300/raw/master/Images/Design.png)

## Files  
Below is an overview of what is contained in each folder, presented in the recommended order of viewing.

**Scripts**  
The "Scripts" folder contains the Python scripts for automated subreddit scraping, comment data cleaning, and visualization generation.  You can run any of them from the command line with the argument "--help" to see their required inputs.  Also note that a configuration file is needed to parse a user's Reddit account information.  The format of this configuration file is as follows:  

[Reddit]  
client_id =  
client_secret =   
password =   
user_agent =   
username =   

Here's a description of each Script and its use cases:  

*scrape_comments.py*  
Scrape comments from Reddit using PRAW, a registered Reddit account, and a valid Reddit dev application.  Scraped comments will be stored in .json format in appropriate folders, under the "Raw" section.  

*clean_comments.py*  
Apply text processing to scraped comment dataset.  All stop words are removed, and text is either stemmed or lemmatized as specified by the user.

*generate_visualizations.py*  
Generate all user-specified data visualizations for cleaned comments.  

**Notebooks**  
The Notebooks folder contains the Jupyter Notebooks that detail the data analysis and clustering steps.  Here's a description of each notebook and what it contains:  

*Train Embeddings*  
This notebook demonstrates how to train document embeddings on our Reddit text dataset.

*Exploratory Data Analysis*  
This notebook contains the Exploratory Data Analysis that will help guide the creation of our clustering models.

*Subreddit Clustering*  
This notebook explores clustering on subreddit text data as scraped and processed earlier.

*Post Clustering*  
This notebook explores clustering on post text data as scraped and processed earlier.

*Code Demonstration*  
Short demonstration of Project code.  Quick way to produce 1-gram visualizations and get recommendations using Agglomerative Clustering and Affinity Propagation.

*Clustering Exploration*  
This notebook contains a general overview of some clustering methods applied to the text dataset.

**Data**  
This folder contains the raw and processed (including lemmatized and stemmed) .json files for each subreddit (organized by category) and trained gensim document embeddings.  

**Images**  
This folder contains visualizations produced by the generate_visualizations.py script.
