# Natural Language Processing

Improving customer satisfaction  for Currys PC World by using Twitter sentiment analysis

## Overview

- This repository contains a customer analysis project for the MSc Business Analytics at the University of Edinburgh commissioned by Dixons Carphone 
- The project obtained public consumer sentiment about Currys PC World from Twitter, to observe what words are frequently related to positive and negative opinions
- Based on the outcomes, actionable recommendations were presented to staff of Dixons Carphone in March 2018.
- The code consists of:
  1. The live Twitter crawler script (similar to [the other uploaded Twitter crawler script](https://github.com/oliverk1/live-twitter-crawler)
  2. The pre-processing steps that were taken to clean the Twitter data and to obtain test/training set. 
  3. Code for applying the various sentiment analysis techniques to the testset.
  4. Code for applying the various sentiment analysis techniques to the entire dataset.
  5. Code for obtaining the most frequent words.
- The most important packages used in this analysis are: Natural Language Toolkit (NLTK) and TextBlob (sentiment analysis)
- It is recommended to run each section as a separate Python file.

## Pre-processing steps taken

Tweets are known for their linguistic complexity as they contain very informal and noisy language. As a result, they require extensive pre-processing to ensure higher accuracy during sentiment analysis (Bao et al., 2014). The shortness of Tweets caused by the 280-character limit encourages the use of abbreviations (e.g. ‘lol’ for ‘laughing out loud’), slang (e.g. ‘meh’ to express disappointment) and emoticons (e.g. 😊 to express happiness) which cannot easily be analysed by sentiment analysis tools. Furthermore, Tweets will often contain grammatical or spelling errors (e.g. ‘hellooooo’ instead of ‘hello’), URLs to (external) media and hashtags (#) to denote certain topics. 

For this analysis, several text normalisation techniques are applied. The NLTK TweetTokenizer is used to tokenize each tweet, remove usernames and replace repeated character sequences greater than 3, with sequences of length 3. Table 4.1 provides an overview of how all (other) objects are handled. Stemming and lemmatisation techniques were explored through the LancasterStemmer and WordNetLemmatizer respectively but resulted in severe errors within tokens and were therefore not applied to the data.
