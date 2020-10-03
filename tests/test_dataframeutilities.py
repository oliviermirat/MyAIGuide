import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from MyAIGuide.utilities.dataFrameUtilities import (
    subset_period,
    insert_data_to_tracker_mean_steps,
    adjust_var_and_place_in_data,
    insert_rolling_mean_columns,
    insert_relative_values_columns
)


def create_test_dataframe(start_date, num_periods):
    """This creates a dummy dataframe for testing. It has date index
    starting at given start date with a number of periods.

    Params:
        start_date: initial date for the index
        num_periods: number of index values

    """
    i = pd.date_range(start_date, periods=num_periods, freq='1D')
    sLength = len(i)
    empty = pd.Series(np.zeros(sLength)).values
    d = {
        'col1': empty + 1,
        'col2': empty + 3,
        'tracker_mean_steps': empty
    }
    return pd.DataFrame(data=d, index=i)


def test_subset_period():
    # create empty (full of 0s) test dataframe
    test_data = create_test_dataframe('2020-07-01', 4)
    # only 1 day
    period1 = ('2020-07-01', '2020-07-01')
    # usual period of more than 1 day
    period2 = ('2020-07-01', '2020-07-02')
    # wrong period with start_date > end_date
    period3 = ('2020-07-01', '2020-06-30')

    # generate expected dataframes
    expected_data1 = create_test_dataframe('2020-07-01', 1)
    expected_data2 = create_test_dataframe('2020-07-01', 2)
    expected_data3 = create_test_dataframe('2020-07-01', 0)

    # run the function with the test data
    result1 = subset_period(test_data, period1[0], period1[1])
    result2 = subset_period(test_data, period2[0], period2[1])
    # attention, function does not raise warning when start_date > end_date
    result3 = subset_period(test_data, period3[0], period3[1])

    # compare results and expected dataframes
    assert_frame_equal(result1, expected_data1)
    assert_frame_equal(result2, expected_data2)
    assert_frame_equal(result3, expected_data3)


def test_insert_data_to_tracker_mean_steps():
    # create empty (full of 0s) test dataframe
    test_data = create_test_dataframe('2020-07-01', 4)
    # only 1 day
    period1 = ('2020-07-01', '2020-07-01')
    # usual period of more than 1 day
    period2 = ('2020-07-01', '2020-07-02')
    # wrong period with start_date > end_date
    period3 = ('2020-07-01', '2020-06-30')

    # generate expected dataframes
    expected_data1 = create_test_dataframe('2020-07-01', 4)
    expected_data1['tracker_mean_steps'] = [1.0, 0.0, 0.0, 0.0]
    expected_data2 = create_test_dataframe('2020-07-01', 4)
    expected_data2['tracker_mean_steps'] = [1.0, 1.0, 0.0, 0.0]
    expected_data3 = create_test_dataframe('2020-07-01', 4)

    # run the function with the test data
    result1 = insert_data_to_tracker_mean_steps(period1, test_data, 'col1', 'tracker_mean_steps')
    result2 = insert_data_to_tracker_mean_steps(period2, test_data, 'col1', 'tracker_mean_steps')
    # attention, function does not raise warning when start_date > end_date
    result3 = insert_data_to_tracker_mean_steps(period3, test_data, 'col1', 'tracker_mean_steps')

    # compare results and expected dataframes
    assert_frame_equal(result1, expected_data1)
    assert_frame_equal(result2, expected_data2)
    assert_frame_equal(result3, expected_data3)


def test_adjust_var_and_place_in_data():
    # create empty (full of 0s) test dataframe
    test_data = create_test_dataframe('2020-07-01', 4)
    # only 1 day
    period1 = ('2020-07-01', '2020-07-01')
    # usual period of more than 1 day
    period2 = ('2020-07-01', '2020-07-02')

    # generate expected dataframes
    expected_data1 = create_test_dataframe('2020-07-01', 4)
    expected_data1['tracker_mean_steps'] = [3.0, 0.0, 0.0, 0.0]
    expected_data2 = create_test_dataframe('2020-07-01', 4)
    expected_data2['tracker_mean_steps'] = [3.0, 3.0, 0.0, 0.0]

    # run the function with the test data
    result1 = adjust_var_and_place_in_data(period1, test_data, 'col1', 'col2', 'tracker_mean_steps')
    result2 = adjust_var_and_place_in_data(period2, test_data, 'col1', 'col2', 'tracker_mean_steps')

    # compare results and expected dataframes
    assert_frame_equal(result1, expected_data1)
    assert_frame_equal(result2, expected_data2)


def test_insert_rolling_mean_columns():
    # create test dataframe
    test_data = create_test_dataframe('2020-07-01', 4)
    test_data['col3'] = [1, 2, 3, 2]

    # generate expected dataframes
    expected_data = test_data.copy()
    expected_data['col1'] = [0.0, 0.0, 0.0, 0.0]
    expected_data['col1_RollingMean'] = [np.nan, 0, 0, 0]
    expected_data['col3'] = [0, 0.5, 1, 0.5]
    expected_data['col3_RollingMean'] = [np.nan, 0.25, 0.75, 0.75]

    # run the function with the test data
    result = insert_rolling_mean_columns(test_data, ['col1', 'col3'], 2)

    # compare results and expected dataframes
    assert_frame_equal(result, expected_data)


def insert_relative_values_columns():
    # create test dataframe
    test_data = create_test_dataframe('2020-07-01', 10)
    test_data['incr_col'] = range(1, 1 + len(test_data))

    # generate expected dataframes
    expected = test_data.copy()

    # case when data is constant, the result is constant 1
    x1 = np.zeros(10) + 1
    x1[0:3] = np.nan
    expected['col2_relative_2_4'] = x1

    # case when incremental data
    x2 = [np.nan, np.nan, np.nan, 1.400000, 1.285714, 1.222222, 1.181818, 1.153846, 1.133333, 1.117647]
    expected['incr_col_relative_2_4'] = x2

    # case when data is full of zeroes
    x3 = np.empty(10)
    x3[:] = np.nan
    expected['tracker_mean_steps_relative_2_4'] = x3

    # run the function with the test data
    result = insert_relative_values_columns(test_data, ['col2', 'incr_col', 'tracker_mean_steps'], 2, 4)

    # compare results and expected dataframes
    assert_frame_equal(result, expected)
