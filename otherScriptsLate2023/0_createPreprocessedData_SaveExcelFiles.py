start_time = "2022-05-10T00:00:00"
end_time = "2022-05-10T23:59:59"

df_fitbit_calories2 = df_fitbit_calories[(df_fitbit_calories['dateTime'] >= start_time) & (df_fitbit_calories['dateTime'] <= end_time)].copy()

def remove_timezone(dt):
  return dt.replace(tzinfo=None) if dt else dt

df_fitbit_calories2['dateTime'] = df_fitbit_calories2['dateTime'].apply(remove_timezone)

df_fitbit_calories2.to_excel("fitbit.xls")

###

dfCycling['startTimestamp'] = dfCycling['startTimestamp'].apply(remove_timezone)
dfCycling['endTimestamp']   = dfCycling['endTimestamp'].apply(remove_timezone)
dfCycling.to_excel("cycling.xls")

