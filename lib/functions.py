import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import os
import time
import datetime as dt


def choose_language(language_options):
    if language_options == "English":
        return "en"
    else:
        return "de"


def get_company(company):

    language_options = ["Deutsch","English"]
    user_language=language_options[0]  # Currently fixed, allow language choice later
    language= choose_language(user_language)

    query_url = "https://www.trustpilot.com/search?query="+company

    choice_request = requests.get(query_url)
    choice = BeautifulSoup(choice_request.text, 'html.parser')
    options = choice.select('div > h3 > a')

    url_choice=[]
    for o in range(len(options)):
        url_choice.append(f"https://www.trustpilot.com{options[o]['href']}?languages={language}")

    return url_choice


def get_basics(user_url_choice):

    # Use the selected Company
    url_chosen = user_url_choice
    count_request = requests.get(url_chosen)
    soup_init = BeautifulSoup(count_request.text, 'html.parser')

    # Get number of feedback pages for website
    selection=soup_init.select('#__next > div > main > div > div.styles_mainContent__nFxAv > section > div.styles_pagination__6VmQv > nav > a')
    pages=int(selection[len(selection)-2]['aria-label'][12:])

    # Get list of all URLs to Scrape
    urllist=[]
    for p in range(1,pages+1):
        if p == 1:
            urllist.append(url_chosen)
        else:
            urllist.append(url_chosen+"&page="+str(p))

    # Get general Information for layout

    get_logo=str(soup_init.select('#__next > div > main > div > div:nth-child(3) > div.styles_wrap__bEQ8l.styles_wrapperBase__O8HY_.styles_withMobilePagination__IdPoO.styles_withHeader__ZC7W8.styles_businessUnitHeader__T06Af > div > div > div > section.styles_businessInformation__6ks_E > div.styles_summary__gEFdQ > div.profile-image_imageWrapper__kDdWe > a > picture > img'))
    logo_link=re.search("(?P<url>https?://[^\s]+)", get_logo).group("url")[:-4]

    overall_rating=str(soup_init.select('#business-unit-title > div > div > p')[0].get_text())+" out of 5"

    features =[elem.get_text() for elem in soup_init.find_all('div', class_='styles_activityCard__aqGtn')]
    claimed = features[0]
    requestor = features[1]
    #resrate= features[3]
    #restime=features[4]

    return urllist, logo_link, overall_rating, claimed, requestor


def create_dataframe(urllist,url_chosen):

    revlist = []   
    namelist = []
    titlelist = []   
    ratlist = []
    datelist = []

    for u in urllist:
        test = requests.get(u)
        feedbacksoup = BeautifulSoup(test.text, 'html.parser')

        # Get Names of Reviewers
        nametags= feedbacksoup.select('article > aside > div > a > div:first-child')
        namelist.extend([n.get_text() for n in nametags])

        # GET FEEDBACK CONTENT
        content=feedbacksoup.find_all('div', class_="styles_reviewContent__0Q2Tg")
        revlist.extend([p.get_text() for p in content])

        # Get Titles and clean it from the Review Content
        titles = feedbacksoup.select('div > h2') 
        titlelist.extend([len(t.get_text()) for t in titles[2:]])

        # GET REVIEW STARS
        ratings=feedbacksoup.find_all('div', class_="star-rating_starRating__4rrcf star-rating_medium__iN6Ty")
        ratlist.extend(["\n".join([img['alt'][6:7] for img in r.find_all('img', alt=True)]) for r in ratings[1:]])
            
        # Get Feedback Date
        dates = feedbacksoup.find_all('time', class_="")
        datelist.extend([d['datetime'] for d in dates])

    # Create Final Dataframe with all information of the Feedbacks
    review_df = pd.DataFrame({"date":datelist,"reviewer":namelist,"text":revlist, "stars":ratlist})
    review_df['company'] = url_chosen[33:] 

    # Cleaning of Text by getting rid of the title out of the text (often duplicate of the beginning of the text)
    clean_content = []
    for text, kill in zip(review_df['text'],titlelist):
        clean_content.append(text[kill:])

    review_df['text']=clean_content

    return review_df


def file_path(url_chosen):
    filepath_input=url_chosen[30:].split("?")[0][4:-3].replace("www.","")
    filepath=f"/Users/robertkammerer/Ironhack/Final Project/data/{filepath_input}.csv"
    return filepath


def decision_path(urllist,url_chosen):

    filepath=file_path(url_chosen)

    if os.path.exists(filepath):
        if dt.date.fromtimestamp(os.path.getmtime(filepath)) > dt.date.today()- dt.timedelta(days=7):
            # Database is up to date -> use existing file
            df=pd.read_csv(filepath)
        else:
            # Database is outdated -> delete old file, scrape new data and save it
            os.remove(filepath)
            print('old data removed')
            df=create_dataframe(urllist,url_chosen)
            df.to_csv(filepath, index=False)
    else:
        df=create_dataframe(urllist,url_chosen)
        df.to_csv(filepath, index=False)

    return df


def preprocessing(review_df):

    # Convert Dates
    review_df['date']=[pd.to_datetime(da[:10], format='%Y-%m-%d') for da in review_df['date']]

    # Add Cluster for positive/negative feedback
    review_df["pos/neg"]= review_df['stars'].astype(str).apply(lambda x: "positive" if x =="5" else ("negative" if x in ["1","2"] else "neutral"))

    # Convert stars to int
    review_df['stars'] = review_df['stars'].astype(int)

    # Add year and month
    review_df['year'] = [elem.year for elem in review_df['date']]
    review_df['year/month'] = review_df['date'].dt.strftime('%Y-%m')
    review_df['month'] = [elem.month for elem in review_df['date']]

    return review_df



