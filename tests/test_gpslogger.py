from MyAIGuide.data.gpslogger import get_gpslogger_activities
import pandas as pd
import numpy as np
from pathlib import Path

TEST_DIR = Path('./data/raw/ParticipantData/Participant1PublicOM/GPSData/Participant1/GPSdata')

i = pd.date_range("2015-12-28", periods=1604, freq="D")
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
}
data = pd.DataFrame(data=d, index=i)


def test_get_gpslogger_activities():
    new_data = get_gpslogger_activities(fname=TEST_DIR, data=data)
    assert isinstance(new_data, pd.DataFrame)
    assert sum(new_data["elevation_gain"]) > 0
