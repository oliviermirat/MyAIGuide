import subprocess

# Retrieving Garmin data

subprocess.run(["python", "loginGarmin.py"])

subprocess.run("python garmindb_cli.py --all --download --import --analyze --latest", shell=True)
