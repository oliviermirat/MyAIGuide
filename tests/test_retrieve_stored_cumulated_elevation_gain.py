#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:58:49 2020

@author: anniewong
"""
#%% 
import pandas as pd
import numpy as np 
from MyAIGuide.data.calculateCumulatedElevationGainMoves import retrieve_stored_CEG_moves

#%% 
# path to file
cev_p1 = "data/raw/ParticipantData/Participant1PublicOM/cum_gains_moves_participant1.csv"

# Create master dataframe
i = pd.date_range("2017-05-19", periods=1200, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "steps": empty,
    "denivelation": empty,
    "kneePain": empty,
    "handsAndFingerPain": empty,
    "foreheadAndEyesPain": empty,
    "forearmElbowPain": empty,
    "aroundEyesPain": empty,
    "shoulderNeckPain": empty,
    "movesSteps": empty,
    "googlefitSteps": empty,
    "elevation_gain": empty,
    "elevation_loss": empty,
    "calories": empty,
    "cum_gain_running": empty,
    "cum_gain_walking": empty,
    "cum_gain_cycling":empty,
}

data = pd.DataFrame(data=d, index=i)

#%% 

def test_retrieve_stored_cumulated_elevation_gain():
    new_data = retrieve_stored_CEG_moves(fname=cev_p1, data=data)
    assert isinstance(new_data, pd.DataFrame)
    assert len(new_data["cum_gain_walking"]) > 0
    assert len(new_data["cum_gain_cycling"]) > 0
    
    # Participant 2 does not have running data
    # Participant 1 has running data for one day, but the CEV equals to 0
    if "cum_gain_running" in new_data.columns:
            assert len(new_data["cum_gain_running"]) > 0