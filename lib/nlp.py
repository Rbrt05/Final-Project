# General Libararies
import numpy as np
import pandas as pd

# Text cleaning
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Graphical libraries
import streamlit as st
import matplotlib.pyplot as plt


def clean_up(s):
    s = str(s).lower().replace("\\","").replace("_"," ")
    # Replace urls by ''
    s = re.sub(r'http\S+', ' ' , s) 
    s = re.sub(r'\W+',' ',s) # Replace everything non-alpahnumeric by ' '
    s = re.sub(r'\d+',' ',s) # Replace one or more digits by  ' '
    s = re.sub(r'([a-z0-9+._-]+@[a-z0-9+._-]+\.[a-z0-9+_-]+)'," ", s) # Replace e-mails by ''
    s = re.sub(r'\s+',' ',s) # Replace one or more whitespaces by  ' '
    return s


def append_stops(string):
    #open list of stopwords
    file = open("/Users/robertkammerer/Ironhack/Final Project/lib/stopwords.csv", "r")
    file_lines = file.read()
    rk_stopwords = file_lines.split("\n")

    #add stopword
    rk_stopwords.append(string)

    #safe amended list
    with open('/Users/robertkammerer/Ironhack/Final Project/lib/stopwords.csv', "w") as file:
        file_lines = "\n".join(rk_stopwords)
        file.write(file_lines)


################################################################
## Spacy Model - better performance, but slightly worse results
################################################################ 

def spacy_cleaner(column):

    #Clean Data
    cleaned_column=column.apply(lambda x: clean_up(x))

    #Create clean corpus
    clean_corpus = ' '.join(str(v) for v in cleaned_column)
    clean_corpus = re.sub(r'\s+',' ', clean_corpus)

    #Use Spacy pretrained model
    import spacy
    spacy_nlp= spacy.load('de_core_news_md')
    doc = spacy_nlp(clean_corpus)

    # manual stopwords
    #Open list of stopwords
    file = open("/Users/robertkammerer/Ironhack/Final Project/lib/stopwords.csv", "r")
    file_lines = file.read()
    rk_stopwords = file_lines.split("\n")

    lemmas = []
    for token in doc:
        if token.orth_ not in rk_stopwords:
            lemmas.append(token.lemma_)

    # Corpus Creation
    lemmas_text = ' '.join(str(v) for v in lemmas)

    return lemmas_text



#############################################
## NLTK Option - Not used due to performance
############################################# 


def tokenize(s):
    #from nltk.tokenize import word_tokenize
    tokenized = word_tokenize(s, language='german')
    return tokenized

def remove_stopwords(l):
    #from nltk.corpus import stopwords
    stop_words = list(stopwords.words('german'))
    for i in range(len(stop_words)):
      stop_words[i] = re.sub(r"\s*'\s*\w*","",stop_words[i])

    cleaned = [(word) for word in l if word not in stop_words]

    return cleaned


def nltk_cleaner(column):
    # import NLP libs
    import nltk
    from bs4 import BeautifulSoup
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('tagsets')
    nltk.download('omw-1.4')

    #Clean Data
    cleaned_column=clean_up(column)

    #Run Tokenizer
    toks=tokenize(cleaned_column)

    #Run Hanover Tagger
    from HanTa import HanoverTagger as ht
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    lemmed = [tagger.tag_sent(toks,taglevel= 1)]
    lemmed
    hanta_lemma=[word[1] for sent in lemmed for word in sent]

    #Stopwords and corpus
    hanta_lemma_stop = remove_stopwords(hanta_lemma)
    
    return hanta_lemma_stop

# Create Corpus
#hanta_text = " ".join(word for word in hanta_lemma_stop)
#hanta_text



######################
## Wordcloud Function
######################


def my_wordcloud(data, title=None):
    #import streamlit as st
    #import matplotlib.pyplot as plt
    from wordcloud import WordCloud, STOPWORDS
    stopwords = STOPWORDS   

    wordcloud=WordCloud(
        background_color='white',
        stopwords = stopwords,
        max_words=20,
        max_font_size=40,
        scale=5,
        random_state=2).generate(str(data))

    

    fig = plt.figure(1, figsize=(20,20))
    fig.clear()

    ax = fig.add_subplot(111)
    plt.axis('off')
    if title:
        ax.set_title(title, fontdict={'fontsize': 25, 'color': '#000000'}, pad=15)

    plt.imshow(wordcloud)

    st.pyplot(fig)

#output=my_wordcloud() -> None