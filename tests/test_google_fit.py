from unittest import TestCase

from MyAIGuide.data import GoogleFitDataJSON, DATA_DIR, get_google_fit_steps
import pandas as pd
import numpy as np

TEST_PARTICIPANT = DATA_DIR / 'Participant2Anonymized'

i = pd.date_range("2015-11-19", periods=1550, freq="1D")
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
}
data = pd.DataFrame(data=d, index=i)


def test_get_google_fit_steps():
    new_data = get_google_fit_steps(fname=TEST_PARTICIPANT, data=data)
    assert isinstance(new_data, pd.DataFrame)
    assert sum(new_data["googlefitSteps"]) > 0
