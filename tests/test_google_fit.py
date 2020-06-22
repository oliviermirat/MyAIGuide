from MyAIGuide.data import GoogleFitDataTCX, DATA_DIR, get_google_fit_steps, collect_activities_from_dir
import pandas as pd
import numpy as np

TEST_PARTICIPANT = DATA_DIR / 'Participant2Anonymized'

TCX_FILE = "2018-11-05T16_46_19-05_00_PT17M6S_Marche à pied.tcx"
TCX_DIR = DATA_DIR / "Participant1PublicOM" / "GoogleFitData" / "smartphone1" / "Activités"
TEST_TCX = TCX_DIR / TCX_FILE

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


def test_google_fit_data_tcx():
    instance = GoogleFitDataTCX(TEST_TCX)

def test_collect_activities_from_dir():
    df = collect_activities_from_dir(TCX_DIR)
    assert "calories", "elevation_gain" in df
    assert "dateTime", "elevation_loss" in df
