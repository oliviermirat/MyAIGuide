#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:43:38 2020

@author: anniewong
"""
#%% 
import pandas as pd

# User defined dictionaries to map strings to categories

# How participant rated its day
RATING_DICT = {
    'great': ['awesome', 'great'],
    'good':['good day', 'good'],
    'pretty good':['pretty good', 'reasonably good'],
    'ok':['average', 'ok', 'ok day'],
    'ups and downs':['up and down','pain was ok when day was warm. but once it got cold, pain ratcheted up'],
    'not great': ['not great', 'blah', 'not a great']
    }

# Activities participant performed

ACTIVITIES_DICT = {
    'rest':['rest', 'resting', 'nap', 'quiet', 'relaxed'],
    'excercise':['yoga', 'bike', 'too much walking'], #to avoid 'after yesterday walking'
    'medical_appointment':['counseling', 'saw dr', 'doctor', 'medical appointment','acupuncture','accupunture', 'therapy', 'platelets', 'blood test'],
    'selfcare':['massage', 'self care'],
    'household': ['laundry', 'cleaning', 'garden'],
    'social': ['with a friend', 'movie day', 'friends', 'social', 'had some company', 'family', 'saw a play', 'board game'],
    }

#%% Functions

def assign_category(stringslist, dictmap, multiple=True):
    """    
    
    Takes in a list of strings and maps every string to a category 
    based on dictionary input. 
    
    params:
        stringslist: list of strings to assign category to
        dictmap: dictionary that maps a list of strings to categories
        multiple: True if you can have multiple categories
        
    return:
        dictionary where key is string and value is category
        
    """
    
    category={}    
    
    for i in stringslist:
        for key in dictmap:
            for substring in dictmap[key]:
                if substring in i:
                    if multiple:
                        if i in category:
                            if key not in category[i]:
                                category[i].append(key)
                        else:
                            category[i]=[key]
                    else:
                        if i not in category:
                            category[i]=[]
                            category[i]=key
                        else:
                            category[i]=key
    return category
   
    
def retrieve_diary_categories(diaryfile):
    """This function takes in participants8 diary and assigns 
    two extra columns 'day_rating' and 'activities' to it 
    
    params:
        diaryfile=path to diary of participant8
        
    return:
        diary: dataframe of diary with extra columns day_rating and activities
    
    
    """
    diary = pd.read_csv(diaryfile, header = None, names=['diarynotes','date'], parse_dates=['date'])
    diary.set_index('date', inplace=True)
    
    # All diarynotes to lowercase for mapping
    diary['diarynotes']=diary['diarynotes'].str.lower()
    
    # Map diarynotes column to categories
    rating=assign_category(diary['diarynotes'].tolist(), RATING_DICT, multiple=False)
    activities=assign_category(diary['diarynotes'].tolist(), ACTIVITIES_DICT)
    
    # Map column to dict 
    diary['activities']=diary['diarynotes'].map(activities)
    diary['rating']=diary['diarynotes'].map(rating)

    return diary


def store_retrieve_diary(data, diaryfile):
            
    """This function updates a dataframe with the diary
    data for participant8
    
    Params:
        diaryfile: path to diary
        data:  pandas dataframe to store data 
        
    Returns:
        data: dataframe data updated with diary data
        """
        
    diary=retrieve_diary_categories(diaryfile)
    data=data.combine_first(diary)
    data.update(diary)
    
    return data
    
    
    