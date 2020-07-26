#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 16:02:45 2020

@author: anniewong
"""

import pandas as pd
import numpy as np

from MyAIGuide.data.store_diary_participant8 import store_retrieve_diary

diaryfile="data/external/myaiguideconfidentialdata/Participant8/Participant8diaries.json"

#%% Creation of the dataframe where everything will be stored
dates = pd.date_range("2019-11-26", periods=175, freq="1D")

columnnames = [
        "diarynotes",
        "rating",
        "activities"     
           ]

data = pd.DataFrame(np.nan, columns = columnnames, index = dates)


def test_get_diary_data():
    new_data=store_retrieve_diary(data,diaryfile)
    assert isinstance(new_data, pd.DataFrame)
    assert len(new_data["diarynotes"]) > 0
    assert len(new_data["activities"]) > 0
    assert len(new_data["rating"]) > 0


