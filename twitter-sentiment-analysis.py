#######################################################################
#   
#   University of Edinburgh Business School
#   MSc Business Analytics
#   Media & Web Analytics
#
#   A sentiment analysis for Currys PC World by using Twitter data
#
#   Please read attached 'Report' file for the analysis and more information
#
#   Copyright© of this project is with the authors
#
#   This code is separated into various stages:
#       1. Code used to scrape Tweets in tweepy
#       2. Code used for pre-processing the data and obtaining testset
#       3. Code used to perform sentiment analysis on testset
#       4. Code used to perform sentiment analysis on entire dataset
#       5. Code used to obtain frequent words 
#
#   It is recommended to run each section as a separate Python file.
#
#######################################################################

#######################################################################
#
#            Section 1. Code used to scrape Tweets in tweepy
#
#######################################################################


# Import packages
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from datetime import datetime
from bs4 import BeautifulSoup
from redis import Redis
from rq import Queue
import pandas as pd
import json
import time
import multiprocessing

# Consumer key, consumer secret, access token, access secret.
# Note: left empty for security reasons

ckey= ""
csecret= ""
atoken= ""
asecret= ""

# The code works with tweepy's StreamListener function, which obtains all tweets as they are posted live.
# This script was placed on a remote server to ensure continuous data collection.

# Error handling through try-and-except. In every try-and-except, all errors are passed.
try: 
    class listener(StreamListener):

        def on_data(self, data):

            try:
                # Get data in json format
                all_data = json.loads(data)   
                ttime = (time.strftime("%H:%M:%S"))
                date = (time.strftime("%d/%m/%Y"))

                # Define user variables
                user_actualname  = all_data["user"]["name"]
                user_lang = all_data["user"]["lang"]
                tweettext = tweet

                # FINDING THE TWEET TEXT
                # Regular Tweet
                tweet = all_data['text']

                # Obtain if Retweeted
                retweeted = False
                if tweet.startswith('RT'):
                    retweeted = True

                # Check for Extended tweets
                if "extended_tweet" in all_data:
                    try:
                        tweet = all_data['extended_tweet']['full_text']
                    except:
                        pass

                # Check for Extended or Regular tweets in Retweets
                if "retweeted_status" in all_data:
                    try:
                        tweet = all_data['retweeted_status']['text']
                    except:
                        pass
                    try:
                        tweet = all_data['retweeted_status']['extended_tweet']['full_text']
                    except:
                        pass

                # Add variables to one row in pandas DataFrame
                row = pd.DataFrame({"date": [date], "time" : [ttime], "user_name" : [user_name], "text": [tweet]})

                # Append row with Tweet data to .csv file
                with open('dataset.csv','a', errors='ignore') as datafr:
                    row = row[['date', 'time', 'user_name', 'text']]
                    row.to_csv(datafr, header=False, sep=';', index=False, encoding='ansi')

                # Return True to ensure function keeps running
                return True

            except:
                print("error")
                pass

        def on_error(self, status):
            print(status)

    # Tweepy authentication login
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    # Stream all data with the search terms in strings
    twitterStream = Stream(auth, listener(), tweet_mode='extended')

    # Relevant search terms are defined and only English Tweets are obtained
    twitterStream.filter(track=['currys','curryspcworld','@curryspcworld','#currys','#curryspcworld','currys.co.uk'], languages=['en'])

except:
    print("error 2")
    pass


###############################################################################
#
#    Section 2. Code used for pre-processing the data and obtaining testset
#
###############################################################################



# Import packages
import re
import nltk
import pandas as pd
from dateutil.parser import parse
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# Read file
dataset = pd.read_csv('dataset.csv')

# Iterate through dataset
preprocessed = []
for c in range(len(dataset)):
    # Obtain row
    row = dataset.iloc[c]
    text = row.text

    # Remove hashtags 
    text = re.sub("#[A-Za-z]+", "", text)
    
    # Use NLTK Tweettokenizer to tokenize tweet, remove usernames and 
    # replace repeated character sequences of length 3 or greater with sequences of length 3
    tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
    filtered_words = tokenizer.tokenize(text)
    
    # Remove any 'pic.twitter' URLs
    prefixes = ('pic.','.twitter.')
    for word in filtered_words:
        if word.startswith(prefixes):
            filtered_words.remove(word)
            
    # Remove any URL, even if hidden in e.g. (), {} etc.
    for obje in filtered_words:
        if obje.startswith('http'):
            filtered_words.remove(obje)
    
    # Expand contractions into full text
    contractions = { 
"ain't": "are not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had / he would",
"he'd've": "he would have",
"he'll": "he shall / he will",
"he'll've": "he shall have / he will have",
"he's": "he has / he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how is",
"I'd": "I had / I would",
"I'd've": "I would have",
"I'll": "I shall / I will",
"I'll've": "I shall have / I will have",
"I'm": "I am",
"I've": "I have",
"isn't": "is not",
"it'd": "it had / it would",
"it'd've": "it would have",
"it'll": "it shall / it will",
"it'll've": "it shall have / it will have",
"it's": "it has / it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had / she would",
"she'd've": "she would have",
"she'll": "she shall / she will",
"she'll've": "she shall have / she will have",
"she's": "she has / she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so as / so is",
"that'd": "that would / that had",
"that'd've": "that would have",
"that's": "that has / that is",
"there'd": "there had / there would",
"there'd've": "there would have",
"there's": "there has / there is",
"they'd": "they had / they would",
"they'd've": "they would have",
"they'll": "they shall / they will",
"they'll've": "they shall have / they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we had / we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what shall / what will",
"what'll've": "what shall have / what will have",
"what're": "what are",
"what's": "what has / what is",
"what've": "what have",
"when's": "when has / when is",
"when've": "when have",
"where'd": "where did",
"where's": "where has / where is",
"where've": "where have",
"who'll": "who shall / who will",
"who'll've": "who shall have / who will have",
"who's": "who has / who is",
"who've": "who have",
"why's": "why has / why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you had / you would",
"you'd've": "you would have",
"you'll": "you shall / you will",
"you'll've": "you shall have / you will have",
"you're": "you are",
"you've": "you have"
}

    for item in filtered_words:
        if "'" in item:
            try:
                fullitem = contractions[item]
            except:
                fullitem = item
                pass
            filtered_words[filtered_words.index(item)] = fullitem
    
    #Remove English stopwords from Tweet and join tokens into string
    #filtered_words = [word for word in filtered_words if word not in stopwords.words('english')]
    text = ' '.join(filtered_words)
    
    # Remove any possible remaining URLs
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', "", text)
    
    # Remove punctuation from Tweet
    punctokenizer = RegexpTokenizer(r'\w+')
    text = punctokenizer.tokenize(text)

    # Remove numerical characters from string
    result = [l for l in text if not l.isdigit()]
    numwords = len(result)
    
    # Apply stemming to tokens
    #stemmer = nltk.stem.LancasterStemmer()
    #stemmedtokens = []
    #for t in result:
        #stemmendtoken = stemmer.stem(t)
        #stemmedtokens.append(stemmendtoken)

    # Apply lemmatization to tokens
    #lemmatizer = WordNetLemmatizer()
    #lemmatized = []
    #for to in result:
        #lemmatizedtoken = lemmatizer.lemmatize(to)
        #lemmatized.append(lemmatizedtoken)

    result = ' '.join(result)
    print(result)
    print('\n')

    # Results with < 4 words are not used in the analysis and filtered out later by using .dropna()
    if numwords < 4:
        result = 0
    preprocessed.append(result)
    
# Add preprocessed data column to dataset
preprocessed = pd.DataFrame(preprocessed, columns=['preprocessed_text'])
dataset = pd.concat([dataset,preprocessed], axis=1)

# Remove any Tweets with less than 4 words 
dataset = dataset.loc[dataset['preprocessed_text'] != 0]

# Remove tweets posted by original CurrysPCWorld account
dataset = dataset.loc[dataset['user_name'] != 'curryspcworld']

# Remove test tweets from authors' account
dataset = dataset.loc[dataset['user_name'] != 'olll_k']

# Create dataset without retweets 
dataset_withoutrts = dataset.loc[dataset['retweeted'] != True]

# Create testset for sentiment analysis of +- 10% (n=500) Tweets
#testset = dataset.sample(n=500)
#testset.to_csv('testset.csv')

# Save datasets to .csv files
dataset.to_csv('preprocesseddataset.csv')
dataset_withoutrts.to_csv('preprocesseddatasetwithoutrts.csv')

print("The amount of Tweets in the dataset is " + str(len(dataset)))
print("The amount of Tweets in the dataset without retweets is " + str(len(dataset_withoutrts)))



#############################################################################
#
#        Section 3. Code used to perform sentiment analysis on testset
#
#############################################################################




import pandas as pd
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from aylienapiclient import textapi

# Credentials of the aylienapiclient API, left blank for security purposes
application_id = ""
application_key = ""

# Set up an instance of the aylienapiclient text API
client = textapi.Client(application_id, application_key)

# Initialize variables
pos = 0
neg = 0
neu = 0
pol = 0
sub = 0

# Number of tweets in total
noOfre = 0

# Number of correct labels
global rightlabel
rightlabel = 0


# Define the function of checking correct labels
def checklabel(sentiment, lab):
    global rightlabel
    if (sentiment == "positive" and lab == 1) or (sentiment == "negative" and lab == -1) or (
            sentiment == "neutral" and lab == 0):
        rightlabel += 1


# Read text and open files to write the results in
testset = pd.read_csv('testsetlabelled.csv', sep=";")
file_pos = open("re_pos_test.csv", 'w', newline='')
file_neg = open("re_neg_test.csv", 'w', newline='')
file_neu = open("re_neu_test.csv", 'w', newline='')

for num in range(0, len(testset)):
    # Calculate the number of tweets in total
    noOfre += 1

    # Assign columns of the content titled as "text", "label" and "preprocessed_text"
    text_original = testset["text"][num]
    label = testset["sentiment"][num]
    text = testset["preprocessed_text"][num]
    print("\n" + text)

    # Call default PatternAnalyzer from TextBlob
    analysis = TextBlob(text)
    print(analysis.sentiment)

    # Get scores of polarity and subjectivity of sentiment analysis results
    pol = analysis.sentiment.polarity
    sub = analysis.sentiment.subjectivity

    # Calculate the score based on the properties of positive/negative of polarity
    if float(pol) > 0.00:
        score = pol + sub * 0.5
    elif float(pol) < 0.00:
        score = pol - sub * 0.5
    else:
        score = 0

    # The tweet will be defined as positive if either score or polarity is larger than 0.50 (positive with high confidence)
    if float(score) >= 0.50 or float(pol) >= 0.50:
        pos += 1
        category = "positive"
        checklabel(category, label)
        file_pos.write(text + "\n")

    # Second (and third) check might be needed if polarity is less than 0.5 and score is larger than 0.00 (positive with lower confidence)
    elif float(score) > 0.00 and float(pol) < 0.50:

        # Call NaiveBayesAnalyzer from TextBlob
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))

        # Compare p_pos and p_neg (in case the classification is still "pos" when p_pos == p_neg)
        # The text is classified as positive if the results match
        if analysis2.sentiment.p_pos > analysis2.sentiment.p_neg:
            pos += 1
            category = "positive"
            checklabel(category, label)
            file_pos.write(text + "\n")
        # Third check is needed
        else:
            # Call Text Analysis API
            response = client.Sentiment({'text': text})
            print("API: " + str(response))

            # Finally define the classification of the text
            if response['polarity'] == "positive":
                pos += 1
                category = "positive"
                checklabel(category, label)
                file_pos.write(text + "\n")
            elif response['polarity'] == "negative":
                neg += 1
                category = "negative"
                checklabel(category, label)
                file_neg.write(text + "\n")
            else:
                neu += 1
                category = "neutral"
                checklabel(category, label)
                file_neu.write(text + "\n")

    # The tweet will be defined as negative if either score or polarity is less than -0.50 (negative with high confidence)
    elif float(score) <= -0.50 or float(pol) <= -0.50:
        neg += 1
        category = "negative"
        checklabel(category, label)
        file_neg.write(text + "\n")

    # Second (and third) check might be needed if polarity is larger than -0.5 and score is less than 0.00 (negative with lower confidence)
    elif float(score) < 0.00 and float(pol) > -0.50:
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))

        # The text is classified as negative if the results match
        if analysis2.sentiment.p_pos < analysis2.sentiment.p_neg:
            neg += 1
            category = "negative"
            checklabel(category, label)
            file_neg.write(text + "\n")

        # Third check is needed
        else:
            response = client.Sentiment({'text': text})
            print("API: " + str(response))
            if response['polarity'] == "positive":
                pos += 1
                category = "positive"
                checklabel(category, label)
                file_pos.write(text + "\n")
            elif response['polarity'] == "negative":
                neg += 1
                category = "negative"
                checklabel(category, label)
                file_neg.write(text + "\n")
            else:
                neu += 1
                category = "neutral"
                checklabel(category, label)
                file_neu.write(text + "\n")

    # NaiveBayesAnalyzer is called and provide the final decision if the result from PatternAnalyzer is neutral
    elif float(score) == 0.0 or float(pol) == 0.0:
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))

        if analysis2.sentiment.p_pos > analysis2.sentiment.p_neg:
            pos += 1
            category = "positive"
            checklabel(category, label)
            file_pos.write(text + "\n")

        elif analysis2.sentiment.p_pos < analysis2.sentiment.p_neg:
            neg += 1
            category = "negative"
            checklabel(category, label)
            file_neg.write(text + "\n")

        elif analysis2.sentiment.p_pos == analysis2.sentiment.p_neg:
            neu += 1
            category = "neutral"
            checklabel(category, label)
            file_neu.write(text + "\n")

# Close the files
file_pos.close()
file_neg.close()
file_neu.close()

# Calculate the number of tweets classified into different corpuses with percentage
print("\n" + "Number of positive tweets: " + str(pos) + "(%.2f%%)" %(100 * float(pos)/float(noOfre)))
print("Number of negative tweets: " + str(neg) + "(%.2f%%)" %(100 * float(neg)/float(noOfre)))
print("Number of neutral tweets: " + str(neu) + "(%.2f%%)" %(100 * float(neu)/float(noOfre)))

# Check and print the accuracy
accuracy = rightlabel / noOfre
print("The accuracy of the testing dataset: " + str(accuracy))



###################################################################################
#
#        Section 4. Code used to perform sentiment analysis on entire dataset
#
###################################################################################




import pandas as pd
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from aylienapiclient import textapi

# Credentials of the aylienapiclient API
application_id = ""
application_key = ""

# Set up an instance of the aylienapiclient text API
client = textapi.Client(application_id, application_key)

# Initialize variables
pos = 0
neg = 0
neu = 0
pol = 0
sub = 0

# Number of tweets in total
noOfre = 0

# Read text and open files to write the results in
dataset = pd.read_csv('preprocesseddataset.csv', sep=",", encoding='ISO-8859-1')
file_pos = open("re_pos.csv", 'w', newline='')
file_neg = open("re_neg.csv", 'w', newline='')
file_neu = open("re_neu.csv", 'w', newline='')

for num in range(0, len(dataset)):

    # Calculate the number of tweets in total
    noOfre += 1
    # Assign the column of the content titled as "preprocessed_text"
    text = dataset["preprocessed_text"][num]
    print("\n" + text)

    # Call default PatternAnalyzer from TextBlob
    analysis = TextBlob(text)
    print(analysis.sentiment)

    # Get scores of polarity and subjectivity of sentiment analysis results
    pol = analysis.sentiment.polarity
    sub = analysis.sentiment.subjectivity

    # Calculate the score based on the properties of positive/negative of polarity
    if float(pol) > 0.00:
        score = pol + sub * 0.5
    elif float(pol) < 0.00:
        score = pol - sub * 0.5
    else:
        score = 0

    # The tweet will be defined as positive if either score or polarity is larger than 0.50 (positive with high confidence)
    if float(score) >= 0.50 or float(pol) >= 0.50:
        pos += 1
        category = "positive"
        file_pos.write(text + "\n")
    # Second (and third) check might be needed if polarity is less than 0.5 and score is larger than 0.00 (positive with lower confidence)
    elif float(score) > 0.00 and float(pol) < 0.50:
        # call NaiveBayesAnalyzer from TextBlob
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))

        # Compare p_pos and p_neg (in case the classification is still "pos" when p_pos == p_neg)
        # The text is classified as positive if the results match
        if analysis2.sentiment.p_pos > analysis2.sentiment.p_neg:
            pos += 1
            category = "positive"
            file_pos.write(text + "\n")

        # Third check is needed
        else:
            # call Text Analysis API
            response = client.Sentiment({'text': text})
            print("API: " + str(response))

            # Finally define the classification of the text
            if response['polarity'] == "positive":
                pos += 1
                category = "positive"
                file_pos.write(text + "\n")
            elif response['polarity'] == "negative":
                neg += 1
                category = "negative"
                file_neg.write(text + "\n")
            else:
                neu += 1
                category = "neutral"
                file_neu.write(text + "\n")

    # The tweet will be defined as negative if either score or polarity is less than -0.50 (negative with high confidence)
    elif float(score) <= -0.50 or float(pol) <= -0.50:
        neg += 1
        category = "negative"
        file_neg.write(text + "\n")

    # Second (and third) check might be needed if polarity is larger than -0.5 and score is less than 0.00 (negative with lower confidence)
    elif float(score) < 0.00 and float(pol) > -0.50:
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))

        # The text is classified as negative if the results match
        if analysis2.sentiment.p_pos < analysis2.sentiment.p_neg:
            neg += 1
            category = "negative"
            file_neg.write(text + "\n")
        # Third check is needed
        else:
            response = client.Sentiment({'text': text})
            print("API: " + str(response))
            if response['polarity'] == "positive":
                pos += 1
                category = "positive"
                file_pos.write(text + "\n")
            elif response['polarity'] == "negative":
                neg += 1
                category = "negative"
                file_neg.write(text + "\n")
            else:
                neu += 1
                category = "neutral"
                file_neu.write(text + "\n")

    # NaiveBayesAnalyzer is called and provide the final decision if the result from PatternAnalyzer is neutral
    elif float(score) == 0.0 or float(pol) == 0.0:
        analysis2 = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        print("NB: " + str(analysis2.sentiment))
        if analysis2.sentiment.p_pos > analysis2.sentiment.p_neg:
            pos += 1
            category = "positive"
            file_pos.write(text + "\n")
        elif analysis2.sentiment.p_pos < analysis2.sentiment.p_neg:
            neg += 1
            category = "negative"
            file_neg.write(text + "\n")
        elif analysis2.sentiment.p_pos == analysis2.sentiment.p_neg:
            neu += 1
            category = "neutral"
            file_neu.write(text + "\n")

# Close the files
file_pos.close()
file_neg.close()
file_neu.close()

# Calculate the number of tweets classified into different corpuses with percentage
print("\n" + "Number of positive tweets: " + str(pos) + " (%.2f%%)" %(100 * float(pos)/float(noOfre)))
print("Number of negative tweets: " + str(neg) + " (%.2f%%)" %(100 * float(neg)/float(noOfre)))
print("Number of neutral tweets: " + str(neu) + " (%.2f%%)" %(100 * float(neu)/float(noOfre)))



#######################################################################
#
#            Section 5. Code used to obtain frequent words
#
#######################################################################




import nltk
from nltk.corpus import stopwords

# Find the 20 most frequent words

# Find from positive corpus with retweets
# Read positive corpus with retweets
reviews_pos_rt = open("re_pos.csv", 'r', encoding='ISO-8859-1')

# List words of length between (1,5]
list_pos_rt1 = [words_pos for words_pos in reviews_pos_rt.read().split(" ")
            if words_pos not in stopwords.words("english") and len(words_pos) > 1 and len(words_pos) <= 5]

# Compute the frequency distribution
word_pos_rt = nltk.FreqDist(word.lower() for word in list_pos_rt1)
print("Top twenty words (length > 1 & <= 5) used in positive tweets with retweets : " + str(word_pos_rt.most_common(20)))
reviews_pos_rt = open("re_pos.csv", 'r', encoding='ISO-8859-1')

# List words of length larger than 5
list_pos_rt2 = [words_pos for words_pos in reviews_pos_rt.read().split(" ")
            if words_pos not in stopwords.words("english") and len(words_pos) > 5]

# Compute the frequency distribution
word_pos_rt = nltk.FreqDist(word.lower() for word in list_pos_rt2)
print("Top twenty words (length > 5) used in positive tweets with retweets: " + str(word_pos_rt.most_common(20)))

# Find from positive corpus without retweets
# Read positive corpus without retweets
reviews_pos_withoutrt = open("re_pos_withoutrts.csv", 'r', encoding='ISO-8859-1')

# List words of length between (1,5]
list_pos_withoutrt1 = [words_pos for words_pos in reviews_pos_withoutrt.read().split(" ")
            if words_pos not in stopwords.words("english") and len(words_pos) > 1 and len(words_pos) <= 5]

# Compute the frequency distribution
word_pos_withoutrt1 = nltk.FreqDist(word.lower() for word in list_pos_withoutrt1)
print("Top twenty words (length > 1 & <= 5) used in positive tweets without retweets: " + str(word_pos_withoutrt1.most_common(20)))
reviews_pos_withoutrt = open("re_pos_withoutrts.csv", 'r', encoding='ISO-8859-1')

# List words of length larger than 5
list_pos_withoutrt2 = [words_pos for words_pos in reviews_pos_withoutrt.read().split(" ")
            if words_pos not in stopwords.words("english") and len(words_pos) > 5]

# Compute the frequency distribution
word_pos_withoutrt2 = nltk.FreqDist(word.lower() for word in list_pos_withoutrt2)
print("Top twenty words (length > 5) used in positive tweets without retweets: " + str(word_pos_withoutrt2.most_common(20)))

# Find from negative corpus with retweets
# Read negative corpus with retweets
reviews_neg_rt = open("re_neg.csv", 'r', encoding='ISO-8859-1')
list_neg_rt1 = [words_neg for words_neg in reviews_neg_rt.read().split(" ")

# List words of length between (1,5]
            if words_neg not in stopwords.words("english") and len(words_neg) > 1 and len(words_neg) <= 5]

# Compute the frequency distribution
word_neg_rt1 = nltk.FreqDist(word.lower() for word in list_neg_rt1)
print("Top twenty words (length > 1 & <= 5) used in negative tweets with retweets: " + str(word_neg_rt1.most_common(20)))
reviews_neg_rt = open("re_neg.csv", 'r', encoding='ISO-8859-1')

# List words of length larger than 5
list_neg_rt2 = [words_neg for words_neg in reviews_neg_rt.read().split(" ")
            if words_neg not in stopwords.words("english") and len(words_neg) > 5]

# Compute the frequency distribution
word_neg_rt2 = nltk.FreqDist(word.lower() for word in list_neg_rt2)
print("Top twenty words (length > 5) used in negative tweets with retweets: " + str(word_neg_rt2.most_common(20)))

# Find from negative corpus without retweets
# Read negative corpus without retweets
reviews_neg_withoutrt = open("re_neg_withoutrts.csv", 'r', encoding='ISO-8859-1')

# List words of length between (1,5]
list_neg_withoutrt1 = [words_neg for words_neg in reviews_neg_withoutrt.read().split(" ")
            if words_neg not in stopwords.words("english") and len(words_neg) > 1 and len(words_neg) <= 5]

# Compute the frequency distribution
word_neg_withoutrt1 = nltk.FreqDist(word.lower() for word in list_neg_withoutrt1)
print("Top twenty words (length > 1 & <= 5) used in negative tweets without retweets: " + str(word_neg_withoutrt1.most_common(20)))
reviews_neg_withoutrt = open("re_neg_withoutrts.csv", 'r', encoding='ISO-8859-1')

# List words of length larger than 5
list_neg_withoutrt2 = [words_neg for words_neg in reviews_neg_withoutrt.read().split(" ")
            if words_neg not in stopwords.words("english") and len(words_neg) > 5]

# Compute the frequency distribution
word_neg_withoutrt2 = nltk.FreqDist(word.lower() for word in list_neg_withoutrt2)
print("Top twenty words (length > 5) used in negative tweets without retweets: " + str(word_neg_withoutrt2.most_common(20)))




############################
############################
#
#   End of file
#
############################
############################