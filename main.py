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
for v in response.voices:
		if v.name == "Obama Better":
				obama = v

assert (obama)
# print(obama)


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




def get_mic(duration=5):
	init_rec = sr.Recognizer()
	print("Let's speak!!")
	with sr.Microphone() as source:
			audio_data = init_rec.record(source, duration=duration)
			print("Recognizing your text.............")
			text = init_rec.recognize_google(audio_data)
			return text

def say_eleven_labs(text):
	audio = elabs.generate(voice=obama, text=text)
	elabs.play(audio)

# say_eleven_labs()

while True:
		print("Talk to obama: (5 seconds)")
		try: 
			user_inputted_text = get_mic()
			print(user_inputted_text)

			print("Asking GPT!")
			text = ask_gpt_img(user_text=user_inputted_text)

			print("got ", text)
			say_eleven_labs(text)

			time.sleep(delay)
		except Exception as e:
			continue



print(response.choices[0])