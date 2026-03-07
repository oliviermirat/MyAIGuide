import pandas as pd

def calculate_daily_phone_usage(file_path):
  
  # Try different encodings if the default 'utf-8' doesn't work
  for encoding in ['utf-8', 'ISO-8859-1', 'cp1252']:
      try:
          with open(file_path, 'r', encoding=encoding) as file:
              lines = file.readlines()
          break
      except UnicodeDecodeError:
          continue
  else:
      raise ValueError("Could not decode the file with utf-8, ISO-8859-1, or cp1252 encodings.")
  
  # Find the index of the line where "Date","Usage time" appears
  for i, line in enumerate(lines):
      if '"Date","Usage time"' in line:
          date_line_index = i
          break
  
  # Read the relevant part of the file into a DataFrame
  date_phone_time_data = pd.read_csv(file_path, skiprows=date_line_index, encoding=encoding)
  
  # Filter out rows with invalid date format
  date_phone_time_data['Date'] = pd.to_datetime(date_phone_time_data['Date'], errors='coerce')
  date_phone_time_data = date_phone_time_data.dropna(subset=['Date'])
  
  # Convert the 'Usage time' to minutes and the 'Date' to 'year-month-day' format
  date_phone_time_data['Usage time'] = pd.to_timedelta(date_phone_time_data['Usage time']).dt.total_seconds() / 60
  
  # Replace NA or inf values with 0 and convert to integer
  date_phone_time_data['Usage time'] = date_phone_time_data['Usage time'].fillna(0).astype(int)
  
  date_phone_time_data['Date'] = date_phone_time_data['Date'].dt.strftime('%Y-%m-%d')
  
  # Group by the 'Date' and sum the 'Usage time'
  daily_phone_usage = date_phone_time_data.groupby('Date')['Usage time'].sum().reset_index()
  
  # Last day is incomplete
  daily_phone_usage = daily_phone_usage.drop(daily_phone_usage.index[-1])
  
  return daily_phone_usage