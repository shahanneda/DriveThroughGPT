import os

import elevenlabs as elabs
from dotenv import load_dotenv

load_dotenv()
eleven_labs_api_key = os.environ.get('ELEVEN_LABS_API_KEY')

assert (eleven_labs_api_key)
elabs.set_api_key(eleven_labs_api_key)

response = elabs.voices()

obama = None

for v in response.voices:
    if v.name == "Obama Better":
        obama = v

assert (obama)

print(obama)

audio = elabs.generate(voice=obama, text="The basic API has a limited number of characters. To increase this limit, you can get a free API key from Elevenlabs (step-by-step guide) and set is as environment variable ELEVEN_API_KEY. Alternatively, you can provide the api_key string argument to the generate function, or set it globally in code with:")
elabs.play(audio)
