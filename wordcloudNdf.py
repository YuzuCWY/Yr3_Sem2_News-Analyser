from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
import jieba
import re
from GoogleNews import GoogleNews
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from urllib.parse import urljoin
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime, timedelta ##for setting data crawling limitation
from wordcloud import WordCloud ## create word cloud
import matplotlib.pyplot as plt ## to present word cloud
from PIL import Image ## to save word cloud as png
from urllib.parse import urlparse
import string ## to remove the symbols in strings

## Prediction: performs sentiment analysis using a pre-trained model.
## Word limitation: 200
target_names = ['Negative', 'Positive']
max_length = 200

## Training model
tokenizer = AutoTokenizer.from_pretrained("clhuang/albert-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("clhuang/albert-sentiment")

## This function uses the language.LanguageServiceClient() from the Google Cloud Natural Language API
## to analyze the sentiment of the text.
## It returns a list containing the sentiment score and magnitude.
def emotion(text):
    client = language.LanguageServiceClient()
    sentiment = client.analyze_sentiment(text)
    return [sentiment.score, sentiment.magnitude]


def get_sentiment_proba(text):
    # Prepare our text into tokenized sequence
    inputs = tokenizer(text, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
    # Perform inference on our model
    outputs = model(**inputs)
    # Get output probabilities by applying softmax
    probs = outputs[0].softmax(1)

    response = {'Negative': round(float(probs[0, 0]), 2), 'Positive': round(float(probs[0, 1]), 2)}
    return response

def search(query):

    ## Create empty lists to store the data
    uni_news_titles = []
    uni_sentiment_scores = []
    uni_links = []
    uni_colors = []
    uni_media_name = []
    ##basic setup
    googleNews = GoogleNews()
    googleNews.setlang('zh') # language set as Chinese, avoid Simplified Chinese
    googleNews.setperiod('d')
    googleNews.setencode('utf-8')
    googleNews.clear()

    ##datetime setting
    current_date = datetime.now()
    current_date_str = current_date.strftime('%m/%d/%Y') # Format the current date as 'MM/DD/YYYY'
    start_date = (current_date - timedelta(days=365)).strftime('%m/%d/%Y') #grab data from recent 12 months
    end_date = current_date_str
    print("Start Date:", start_date)
    print("End Date:", end_date)
    googleNews.setTimeRange(start_date, end_date)

    #input search keyword
    googleNews.search(query)

    alldata = googleNews.result()
    result = googleNews.gettext()
    links = googleNews.get_links()


    # Change the number to the desired number of pages
    num_pages = 3
    page = 1

    counter = 1
    unique_results = set()  # Store unique results to avoid duplicates
    
    while page <= num_pages:
        googleNews.getpage(page)
        alldata.extend(googleNews.result())
        result.extend(googleNews.gettext())
        links.extend(googleNews.get_links())
        page += 1

    #print results
    for n in range(len(result)):
        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = get_sentiment_proba(result[n])
        if result[n] not in unique_results:
            unique_results.add(result[n])
            uni_news_titles.append(result[n])
            media_name = urlparse(links[n]).hostname
            uni_media_name.append(media_name)
            uni_links.append(links[n])
            # Extract the value of the '+/-' key
            negative_score = sentiment_scores['Negative']
            positive_score = sentiment_scores['Positive']
            if (negative_score>positive_score):
                uni_colors.append("red")
                uni_sentiment_scores.append(negative_score*-1)
            else:
                uni_colors.append("green")
                uni_sentiment_scores.append(positive_score)
            print("====================", counter, "====================")
            print(sentiment_scores)
            print(result[n])
            print(links[n])
  
            counter += 1
    df = pd.DataFrame({
                'News Title': uni_news_titles,
                'Sentiment Scores': uni_sentiment_scores,
                'Link': uni_links,
                'Media': uni_media_name,
                'Color': uni_colors})
    print(df)
    create_cloud(df, unique_results)

    return(df)

def create_cloud(df, unique_results):
    #set to print the complete df
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(df)
    # Remove symbols and spaces from 'News Title' column
    symbols_to_remove = ['」', '｜', '「', '，', '：', '【', '】',
                         '、', '？', '@', '！',  '）', '（', '／',
                         '》', '《', '。', '︱', '＋', '︳', '’',
                         '｜', '|', '-', '〈', '〉', '-', '︰',
                         "“", "”", "？"]
    df['News Title'] = df['News Title'].apply(lambda x: ''.join([char for char in x if char not in string.punctuation and char != ' ']))
    df['News Title'] = df['News Title'].apply(lambda x: ''.join([char for char in x if char not in symbols_to_remove]))# Remove specific symbols from 'News Title' column
    ##print(df['News Title'].to_list())
    
    # Concatenate the news titles
    text_data = ' '.join(df['News Title'])

    # Set the font that supports Chinese characters
    font_path = 'MSYH.ttc'  

    # Generate word cloud with custom font sizes and disable collocations
    wordcloud = WordCloud(scale=5, background_color="grey", font_path='MSYH.ttc', min_font_size=7, max_font_size=30, collocations=True).generate(text_data)

    # Recolor the word cloud based on the color values in the DataFrame
    color_map = {row['News Title']: row['Color'] for _, row in df.iterrows()}
    wordcloud = wordcloud.recolor(color_func=lambda word, font_size, position, orientation, random_state, **kwargs: color_map.get(word))
    

    # Set the resolution (dpi) of the word cloud image
    dpi = 50  # Adjust the dpi value as needed

    # Set the figure size based on the desired image dimensions
    fig_width = 50  # Adjust the width of the image as needed
    fig_height = 50  # Adjust the height of the image as needed

    # Create a figure with the specified dimensions and dpi
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)

    # Plot the word cloud on the figure
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # Save the word cloud as a PNG image
    output_path = 'pics/wordcloud3.png'  # Replace with the desired output path and filename
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)

    # Display a success message
    print(f"Word cloud saved as '{output_path}'")

    # Show the generated word cloud
    plt.show()
