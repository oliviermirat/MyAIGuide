#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 09:23:24 2020

@author: anniewong

This script plots the data for participant 8

"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")
sns.set_palette("husl")

from MyAIGuide.utilities.dataFrameUtilities import insert_rolling_mean_columns

# Read file 
input = open("../data/preprocessed/preprocessedDataParticipant8.txt", "rb")
data = pickle.load(input)
input.close()

#%%

def preprocess_data_for_plotting(data):
    
    """Preprocess data for plotting"""
    # Date when participant 8 started tracking pain data: 2019-08-12
    data=data.loc["2019-08-12":]
    
    # Add rolling mean columns
    columns=data.columns.tolist()
    data=insert_rolling_mean_columns(data, columns, 21)
    
    # Add average pain column
    pains=["abdominalpain","kneepain", "hippain", "legpain", "handpain", "headache", "lowbackpain"]
    data['average_pain'] = data[pains].mean(axis=1)

    # Create weekly mean dataset
    # Resample to weekly frequency, aggregating with mean
    data_weekly_mean = data.resample('W').mean()
    data_weekly_mean = data_weekly_mean.loc[:,~data_weekly_mean.columns.duplicated()]
    
    return data, data_weekly_mean


def plot_pain_against_steps(data):
    
    """Plots individual pains + happiness against steps and 7 days rolling mean of steps"""
    
    # "lowbackpain" contain too little data for plotting
    cols = ["abdominalpain","kneepain", "hippain", "legpain", "happiness", "handpain", "headache", "lowbackpain"]
    colors = ["dodgerblue", "mediumaquamarine", "navy", "darkorange", "mediumslateblue", "deepskyblue", "teal", "red"]
    
    sns.set()
    fig,axes = plt.subplots(8, sharex=True, sharey=False, figsize=(15,10))
    fig.suptitle("Participant 8: pain and happiness against steps")
    
    # ---- loop over axes ----
    for i,ax in enumerate(data[cols]):
      axes[i].plot(data[cols[i]], label=cols[i], color=colors[i])
      axes[i].plot(data['steps'], label="steps", color="gray")
      axes[i].plot(data['steps_RollingMean'], linestyle='-', label="steps 7 days rolling mean", color="blueviolet")
      axes[i].legend(loc="upper right")
    plt.show()
    
def plot_pains_against_happiness(data, data_weekly_mean):
    
    """
    Plot 1: individual pains against happiness
    Plot 2: average pain against happiness, weekly mean of pains against weekly mean of happiness 
    """
    
    cols = ["abdominalpain","kneepain", "hippain", "legpain", "happiness", "handpain", "headache", "lowbackpain"]
    colors = ["dodgerblue", "mediumaquamarine", "navy", "darkorange", "mediumslateblue", "deepskyblue", "teal", "red"]
    
    sns.set()
    
    # plot 1: daily pains against happiness
    fig,axes = plt.subplots(8, sharex=True, sharey=False, figsize=(15,10))
    fig.suptitle("Participant 8: pains against happiness")
    
    for i,ax in enumerate(data[cols]):
        axes[i].plot(data['happiness'], label="happiness", color="deeppink")
        axes[i].plot(data[cols[i]], label=cols[i], color=colors[i])
        axes[i].legend(loc="upper right")
        
    plt.show()
    
    # Plot 2: weekly pains against happiness
    fig,axes = plt.subplots(2, figsize=(15,10))
    axes[0].title.set_text('Daily mean: pain against happiness')
    axes[0].plot(data['happiness'], label="happiness", color="deeppink")
    axes[0].plot(data['average_pain'], label='average pain', color = "blue")
    axes[0].legend(loc="upper right")
    
    axes[1].title.set_text('Weekly mean: pain against happiness')
    axes[1].plot(data_weekly_mean['happiness'], label="happiness", marker='o', markersize=5, color="deeppink")
    axes[1].plot(data_weekly_mean['average_pain'], label="average pain", marker='o', markersize=5, color="black")
    pains= ["abdominalpain","kneepain", "hippain", "legpain", "handpain", "headache", "lowbackpain"]
    for i,ax in enumerate(data_weekly_mean[pains]):
        axes[1].plot(data_weekly_mean[pains[i]], label=pains[i], marker='o', markersize=1.5, color=colors[i])
        axes[1].legend(loc="upper right")
    
    plt.show()    


def plot_pain_against_rating(data):
    
    """Plot average pain against rating (from diary) """
    
    sns.set(style="darkgrid")
    r=sns.catplot(x="rating_encoded", y="average_pain", kind="swarm", data=data);
    r.set(xticklabels=["not great","ups and downs","ok","pretty good","good","great"])
    
    plt.show()

def plot_pain_against_complaints(data):
    
    """Plot average pain against complaints"""

    fig, axes = plt.subplots(4, 2, figsize=(15, 10), sharey=True, sharex=False)    
    fig.suptitle("Participant 8: complaints against average pain", fontsize=13) 
    sns.scatterplot(x='complaintsawesomeday', y="average_pain", data=data,ax=axes[0,0])
    sns.scatterplot(x='complaintspoorsleep', y="average_pain", data=data,ax=axes[0,1])
    sns.scatterplot(x='complaintsloneliness', y="average_pain", data=data,ax=axes[1,0])
    sns.scatterplot(x='complaintssadness', y="average_pain", data=data,ax=axes[1,1])
    sns.scatterplot(x='complaintsstress', y="average_pain", data=data,ax=axes[2,0])
    sns.scatterplot(x='complaintstired', y="average_pain", data=data,ax=axes[2,1])
    sns.scatterplot(x='complaintsworriedanxious', y="average_pain", data=data,ax=axes[3,0])
    
    plt.tight_layout()


def plot_pain_against_activities(data):
    
    """Plot average pain against activities (from diary)"""
    
    fig, axes = plt.subplots(3, 2, figsize=(15, 10), sharey=True, sharex=False)    
    fig.suptitle("Participant 8: activities against average pain", fontsize=13)
    sns.scatterplot(x="household", y="average_pain", data=data, ax=axes[0,0])
    sns.scatterplot(x="excercise", y="average_pain",data=data, ax=axes[0,1])
    sns.scatterplot(x="medical_appointment", y="average_pain", data=data, ax=axes[1,0])
    sns.scatterplot(x="rest", y="average_pain", data=data, ax=axes[1,1])
    sns.scatterplot(x="selfcare", y="average_pain", data=data, ax=axes[2,0])
    sns.scatterplot(x="social", y="average_pain", data=data, ax=axes[2,1])
    
    plt.tight_layout()


def correlation_plot(data):
    
    """Plot heatmap of correlations for numerical values"""

    sns.set(style="white")
    
    numerical=['abdominalpain', 'complaintsawesomeday',
           'complaintsloneliness', 'complaintspoorsleep', 'complaintssadness',
           'complaintsstress', 'complaintstired', 'complaintsworriedanxious',
           'handpain', 'happiness', 'headache', 'hippain', 'kneepain', 'legpain',
           'lowbackpain', 'steps', 'rating_encoded']
    
    corr = data[numerical].corr()
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=np.bool))
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(15,15))
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
    
    ax.tick_params(axis='both', labelsize=8)
    
    plt.xticks(rotation=45, horizontalalignment="right")
    
    plt.show()

#%% Run code

# step 1: preprocess data for plotting
data, data_weekly_mean =preprocess_data_for_plotting(data)

# step 2: Run functions for plotting 
plot_pain_against_steps(data)
plot_pains_against_happiness(data, data_weekly_mean)
plot_pain_against_rating(data)
plot_pain_against_complaints(data)
plot_pain_against_activities(data)
correlation_plot(data)