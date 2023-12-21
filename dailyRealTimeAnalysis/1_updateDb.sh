# Don't forget to: "conda activate garmindb" first!

# Login with Garmin credentials
python loginGarmin.py

# Only one time at the beginning
# python garmindb_cli.py --all --download --import --analyze

# Updates database
python garmindb_cli.py --all --download --import --analyze --latest

# Occasionally backup
# python garmindb_cli.py --backup
