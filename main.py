import time
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
import elevenlabs as elabs
import speech_recognition as sr
import pyaudio

load_dotenv()  

eleven_labs_api_key = os.environ.get('ELEVEN_LABS_API_KEY')
# Setup eleven labs
assert (eleven_labs_api_key)
elabs.set_api_key(eleven_labs_api_key)
response = elabs.voices()
obama = None
print(response.voices)
for v in response.voices:
		if v.name == "Shahan 1":
				obama = v

assert (obama)
print(obama)


client = OpenAI()
folder = "images"
image_path = f"{folder}/image.png"
cam_port = 0
delay = 5


# response = client.chat.completions.create(
#   model="gpt-4-vision-preview",
#   messages=[
#     {
#       "role": "user",
#       "content": [
#         {"type": "text", "text": "What’s in this image?"},
#         {
#           "type": "image_url",
#           "image_url": {
#             "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
#           },
#         },
#       ],
#     }
#   ],
#   max_tokens=300,
# )

def encode_image(image_path):
	with open(image_path, "rb") as image_file:
		return base64.b64encode(image_file.read()).decode('utf-8')

def ask_gpt_img(user_text):
	base64_image = encode_image(image_path)
	client = OpenAI()
	response = client.chat.completions.create(
		model="gpt-4-vision-preview",
		messages=[
			{
				"role": "user",
				"content": [
					{"type": "text", "text": f"Let's have a friendly conversation. I am the person in the image. First: {user_text}. "},
					{
						"type": "image_url",
						"image_url": {
							"url": f"data:image/jpeg;base64,{base64_image}"
						},
					},
				],
			}
		],
		max_tokens=300,
	)
	res = response.choices[0].message.content
	return res


import io

class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")

import keyboard  # using module keyboard
i = 0

def record(source, duration=None, offset=None):
		global i
		"""
		Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

		If ``duration`` is not specified, then it will record until there is no more audio input.
		"""
		# assert isinstance(source, AudioSource), "Source must be an audio source"
		# assert source.stream is not None, "Audio source must be entered before recording, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"

		frames = io.BytesIO()
		seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
		elapsed_time = 0
		offset_time = 0
		offset_reached = False
		while True:  # loop for the total number of chunks needed
				# print("in loop")
				if os.path.isdir("./stopped"):
					break
				# if i % 1000 == 0:
				# 	print("i " + i)
				# 	break

				# try:  # used try so that if user pressed other than the given key error will not be shown
				# i += 1
				# 	if keyboard.is_pressed('q'):  # if key 'q' is pressed 
				# 			print('You Pressed A Key!')
				# 			break  # finishing the loop
				# except:
				# 		break  # if user pressed a key other than the given key the loop will break

				if offset and not offset_reached:
						offset_time += seconds_per_buffer
						if offset_time > offset:
								offset_reached = True

				buffer = source.stream.read(source.CHUNK)
				# if len(buffer) == 0: break

				if offset_reached or not offset:
						elapsed_time += seconds_per_buffer
						if duration and elapsed_time > duration: break

						frames.write(buffer)

		print("broke out of thread")
		frame_data = frames.getvalue()
		frames.close()
		return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)


def get_mic(duration=5):
	init_rec = sr.Recognizer()
	print("Let's speak!!")
	with sr.Microphone() as source:
			audio_data = record(source)
			print("Recognizing your text.............")
			text = init_rec.recognize_google(audio_data)
			return text

import wave

import wave

def say_eleven_labs(text):
	audio = elabs.generate(voice=obama, text=text)
	elabs.play(audio)

# say_eleven_labs()

# say_eleven_labs("Hello how are you")
print(os.path.isdir("./stopped"))

while True:
		print("Talk to obama: (5 seconds)")
		try:
			try:
				os.removedirs("./stopped")
			except Exception as e:
				pass
			user_inputted_text = get_mic()
			print("got user texted", user_inputted_text)

			print("Asking GPT!")
			text = ask_gpt_img(user_text=user_inputted_text)

			print("got ", text)
			say_eleven_labs(text)
			# x = input()
			# time.sleep(delay)
		except Exception as e:
			print(e)
			continue



print(response.choices[0])