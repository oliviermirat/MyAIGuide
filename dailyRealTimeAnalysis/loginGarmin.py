from getpass import getpass
import garth
import json

with open("info.json", 'r') as json_file:
  info = json.load(json_file)

email    = info["email"]
password = info["password"]

garth.login(email, password)

