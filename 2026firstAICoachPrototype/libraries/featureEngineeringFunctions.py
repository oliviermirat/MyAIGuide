import numpy as np

def featureEngineering(df, CANDIDATES, ONLY_USE_ACWR, ACUTE_WINDOW, CHRONIC_WINDOW, INCLUDE_NB_PREVIOUS_DAY_PAIN, PAIN_TYPE):

  # Feature engineering
  candidateVariables = []
  for s in CANDIDATES:
    if not(ONLY_USE_ACWR):
      df.loc[:, f'{s}_acute']   = df[s].rolling(ACUTE_WINDOW).mean().fillna(0)
      df.loc[:, f'{s}_chronic'] = df[s].rolling(CHRONIC_WINDOW).mean()
    df.loc[:, f'{s}_acwr'] = (df[f'{s}_acute'] / df[f'{s}_chronic'].replace(0, np.nan)).fillna(0)
    if not(ONLY_USE_ACWR):
      candidateVariables.append(f'{s}_acute')
      candidateVariables.append(f'{s}_chronic')
    candidateVariables.append(f'{s}_acwr')

  if INCLUDE_NB_PREVIOUS_DAY_PAIN > 0:
    rolling_pain = df[PAIN_TYPE].rolling(window=INCLUDE_NB_PREVIOUS_DAY_PAIN, min_periods=1).mean()
    col_name = f'{PAIN_TYPE}_avgLast{INCLUDE_NB_PREVIOUS_DAY_PAIN}Days'
    df[col_name] = rolling_pain.shift(1)
    df.loc[df.index[0], col_name] = df[PAIN_TYPE].iloc[0]
    candidateVariables.append(col_name)
  
  return [df, candidateVariables]
