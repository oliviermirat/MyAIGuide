import subprocess

# Saving data on hard drive from WhatPulse and ManicTime

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

subprocess.run(["python", "compareCaloriesAllTime.py"])
