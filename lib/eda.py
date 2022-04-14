# Used Libraries

from this import d
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import time
import datetime as dt
import pandas as pd
import numpy as np


# Plotting the histogram

def histogram(start, end, unit, df):

    st.cache(suppress_st_warning=True)
    #Check the date input
    if start == None:
        start=pd.Timestamp(dt.datetime.today()- dt.timedelta(days=5000))
    else:
        start=pd.Timestamp(start)

    if end == None:
        end=pd.Timestamp(dt.datetime.today())
    else:
        end=pd.Timestamp(end)

    db_filtered = df[(df['date']>=start) & (df['date']<=end)]

    col_palette=color_palette(db_filtered)

    if unit == "month":
        db_final =db_filtered[['year/month', 'stars']]
    else:
        db_final = db_filtered[['year','stars']]

    # Create and format the plot
    fig1, ax1 = plt.subplots(figsize=(15,8))
    sns.set(style="darkgrid")

    #Format Legend
    ax1.legend(loc='upper right', frameon=False, prop={'size': 20})
    plt.rc('legend',fontsize=15)

    # Plot
    sns.histplot(x=db_final.iloc[0:,0].astype(str), hue=db_final['stars'], multiple='stack',
    palette=col_palette,shrink=0.8 )

    # Format axis
    ax1.set_title("Number of Reviews over time", fontdict={'fontsize': 25, 'color': '#000000'}, pad=15)
    ax1.set_ylabel('Count',fontdict={'fontsize': 15, 'color': '#000000'})
    ax1.set_xlabel('',fontdict={'fontsize': 15, 'color': '#000000'})
    ax1.invert_xaxis()
    ax1.tick_params(rotation=45)
    plt.xticks(fontsize=15 )
    plt.yticks(fontsize=15 )

    st.pyplot(fig1)

# Plotting the lineplot 

def lineplot(start, end, unit, df):

    #Check the date input
    if start == None:
        start=pd.Timestamp(dt.datetime.today()- dt.timedelta(days=5000))
    else:
        start=pd.Timestamp(start)
    if end == None:
        end=pd.Timestamp(dt.datetime.today())
    else:
        end=pd.Timestamp(end)

    db_filtered = df[(df['date']>=start) & (df['date']<=end)]

    if unit == "month":
        db_final =db_filtered[['year/month', 'stars', 'pos/neg']].groupby(['year/month']).agg({'pos/neg':'size', 'stars':'mean'}).rename(columns={'pos/neg':'count', "stars":'mean'}).reset_index()
    else:
        db_final = db_filtered[['year','stars', 'pos/neg']].groupby(['year']).agg({'pos/neg':'size', 'stars':'mean'}).rename(columns={'pos/neg':'count', "stars":'mean'}).reset_index()

    fig2, ax1 = plt.subplots(figsize=(15,8))
    sns.set(style="darkgrid")
    sns.lineplot(x=db_final.iloc[0:,0].astype(str), y= db_final['mean'], linewidth=3, color='#003366')
    
    ax1.set_title("Avg. review score cohorts", fontdict={'fontsize': 25, 'color': '#000000'}, pad=15)
    ax1.set_ylabel('Avg. Score',fontdict={'fontsize': 15, 'color': '#000000'})
    ax1.set_xlabel('',fontdict={'fontsize': 15, 'color': '#000000'})
    ax1.tick_params(rotation=45)
    ax1.set_ylim(bottom=0)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    st.pyplot(fig2)  


# Color palette used for the histogram
   
def color_palette(df):
    starlist = df['stars'].unique()
    color_palette = []

    if 1 in starlist:
        color_palette += ['#FF0000']
    if 2 in starlist:
        color_palette += ['#FF8000']
    if 3 in starlist:
        color_palette += ['#FFFF00']
    if 4 in starlist:
        color_palette += ['#00CC00']
    if 5 in starlist:
        color_palette += ['#006633']

    return color_palette
