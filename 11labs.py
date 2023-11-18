import os

import elevenlabs as elabs
import requests
from dotenv import load_dotenv

load_dotenv()
eleven_labs_api_key = os.environ.get('ELEVEN_LABS_API_KEY')

assert (eleven_labs_api_key)
elabs.set_api_key(eleven_labs_api_key)

response = elabs.voices()

for v in response.voices:
    if v.name == "Obama Better":
        obama = v

print(obama)
