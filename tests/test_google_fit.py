from MyAIGuide.data import GoogleFitData, DATA_DIR, get_google_fit_steps

TEST_PARTICIPANT_JSON = DATA_DIR / 'Participant2Anonymized' / 'GoogleFitParticipant2.json'
instance = GoogleFitData(TEST_PARTICIPANT_JSON)


def test_raw_json():
    raw_json = instance._raw_json()
    assert TEST_PARTICIPANT_JSON.exists()
    assert 'bucket' in raw_json


def test__process_json():
    processed_json = instance._process_json()
    first_int = processed_json[0]

    assert isinstance(processed_json, list)
    assert list(first_int.keys()) == ['start_time', 'end_time', 'steps']


def test_df():
    df = instance.df

    # check if we have step data as columns
    assert list(df.columns) == ['GoogleFitSteps']

    # indexed by days
    assert df.index.dtype == 'datetime64[ns]'


def test_get_google_fit_steps():
    df = get_google_fit_steps(TEST_PARTICIPANT_JSON)

    # check if we have step data as columns
    assert list(df.columns) == ['GoogleFitSteps']

    # indexed by days
    assert df.index.dtype == 'datetime64[ns]'
