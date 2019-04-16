import sys
import activity

config_location = sys.argv[1]
with open(config_location,"w") as f:
    configuration = json.load(f)
f.close()

activity(configuration)
