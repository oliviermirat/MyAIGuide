import subprocess

# Saving data on hard drive from WhatPulse and ManicTime

if False:
  
  subprocess.call(['C:\Program Files\WhatPulse\\WhatPulse.exe'])

  input("print when done with WhatPulse saving")

  subprocess.call(['C:\Program Files (x86)\ManicTime\\ManicTime.exe'])

  input("print when done with ManicTime saving")

# Retrieving Garmin data

subprocess.run(["python", "loginGarmin.py"])

subprocess.run("python garmindb_cli.py --all --download --import --analyze --latest", shell=True)

# Launching analysis

subprocess.run(["python", "2_analyze.py"])

# Plotting results

subprocess.run(["python", "3_plotFigs.py"])

# New analysis

if False:

  subprocess.run(["python", "4_highHeartBeatsAnalysis.py"])

  subprocess.run(["python", "5_checkSleepAndHRV.py"])

#

if False:

  subprocess.run(["python", "compareCaloriesAllTime.py"])

# Backuping Garming data
import os
source = r"C:\Users\mirat\HealthData"
destination = r"C:\Users\mirat\OneDrive\QS\GarminDbBackUp"
os.makedirs(destination, exist_ok=True)
os.system(f'xcopy /E /I /Y "{source}" "{destination}"')

# Latest analysis

subprocess.run(["python", "6_condensedNewAnalysis.py"])
subprocess.run(["python", "5_checkSleepAndHRV.py"])
