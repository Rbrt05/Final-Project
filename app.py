###############################
# This program lets you       #
# - Create a dashboard        #
# - Every dashboard page is  #
# created in a separate file  #  
###############################

# Python libraries
import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from reader import feed
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import datetime as dt
import stat
import re

# User module files
from lib.functions import *
from lib.eda import *
from lib.nlp import *

def main():
  
    #############  
    # Main page #
    ############# 


    st.set_page_config(page_title='Trustpilot Review Analyzer',  layout='wide', page_icon='chart_with_upwards_trend')  
    st.title("Trustpilot Review Analyzer")

    col1, col2 = st.columns(2)

    # Get Company Name and return URL
    with col1:
        company_name=  st.text_input('Please insert the name of the company you want to analyse')

    if len(company_name) != 0:
        company_urls = get_company(company_name)

        # Get URL Choice and get Basic informations
        with col2:
            user_url_choice = st.selectbox("Please choose the correct option:", company_urls)
        urllist, logo, overall_rating, claimed, requestor = get_basics(user_url_choice)

    
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            st.image(logo,width=150)

        with col4:
            st.metric("Overall Rating", overall_rating)

        with col5:
            st.metric("Verified Profile", claimed)
        
        with col6:
            st.metric("Activity", requestor[:16])
    
        st.markdown("""---""")  


        # Start workflow
        scraped_df=decision_path(urllist, user_url_choice)

        #Preprocess Data

        final_df = preprocessing(scraped_df)

        col5s, col4s, col3s, col2s, col1s, colcsat = st.columns(6)

        with col5s:
            st.metric("5 Stars", five_stars(final_df))

        with col4s:
            st.metric("4 Stars", four_stars(final_df))
        
        with col3s:
            st.metric("3 Stars", three_stars(final_df))

        with col2s:
            st.metric("2 Stars", two_stars(final_df))

        with col1s:
            st.metric("1 Stars", one_stars(final_df))

        with colcsat:
            st.metric("CSAT", csat(final_df))

        st.markdown("""---""")  

        # Create Visualisations Menu
        st.subheader('Customer reviews over time')

        min_date=dt.date.today()-dt.timedelta(365)
        max_date=dt.date.today()

        colstart, colend, colunit = st.columns(3)

        with colstart:
            startdate=st.date_input("Startdate",value=min_date)

        with colend:
            enddate = st.date_input("Enddate", value=max_date)

        with colunit:
            axis_unit = st.selectbox("Axis unit", ['month','year'])

        # Print Visualisation
        col7, col8 =st.columns(2)
        with col7:
            histogram(startdate, enddate,axis_unit, final_df)
        with col8:
            lineplot(startdate, enddate,axis_unit, final_df)

        st.markdown("""---""") 
        # Print Wordclouds

        st.subheader('Most frequent words in positive an negative feedbacks')

        
        wc_df = final_df.dropna()

        try:
            positive
            if (len(positive)+len(negative)) != len(wc_df):
                corppos = spacy_cleaner(positive)
                corpneg = spacy_cleaner(negative)

                colpos, colneg = st.columns(2)
                with colpos:
                    my_wordcloud(corppos, title='Most used words in positive reviews')
                with colneg:
                    my_wordcloud(corpneg,title = 'Most used words in negative reviews')
            else:
                pass
        except NameError:
            
            positive=wc_df[wc_df['pos/neg']=="positive"]['text']
            negative=wc_df[wc_df['pos/neg']=="negative"]['text']

            corppos = spacy_cleaner(positive)
            corpneg = spacy_cleaner(negative)

            colpos, colneg = st.columns(2)

            with colpos:
                my_wordcloud(corppos, title='Most used words in positive reviews')

            with colneg:
                my_wordcloud(corpneg,title = 'Most used words in negative reviews')

        
        new_stopword = st.text_input('Enter a word that you would like to add to the stoplist')
        
        append_stops(new_stopword)

main()
