import subprocess

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
