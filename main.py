import base64
import io
import json
import os
import queue
import threading
import time
import wave

import elevenlabs as elabs
import keyboard  # using module keyboard
import sounddevice as sd
import soundfile as sf
import speech_recognition
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

eleven_labs_api_key = os.environ.get('ELEVEN_LABS_API_KEY')
wit_api_key = os.environ.get("WIT_API_KEY")

# Setup eleven labs
assert (eleven_labs_api_key)
elabs.set_api_key(eleven_labs_api_key)
response = elabs.voices()

person = "Morgan Freeman"

# obama = response.voices[0]
obama = None
for v in response.voices:
    if v.name == "Morgan Freeman":
        obama = v
if obama is None:
    obama = response.voices[0]

assert (obama)
print(f"Using {obama.name} voice")

client = OpenAI()
folder = "images"
image_path = f"{folder}/image.png"
cam_port = 0
delay = 5

messages: list[dict[str, str]] = [
    {"role": "user", "content": f"""You are a McDonald's drive-through operator and are having a conversation with a customer. Respond as if you were in a real conversation with the customer. Respond in the manner of {person}. \n Output format: {{"response": XXX, "cart_items": []}}.\n JSON object: \n"""}
]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


last_response = ""
yes_philosophy = True


def ask_gpt(user_text: str | None):
    print("Thinking...")
    global messages, last_response, yes_philosophy
    if user_text:
        philosophy_text = ""
        if yes_philosophy:
            philosophy_text = f"Add philosophical thoughts in the manner of {person}."

        # yes_philosophy = not yes_philosophy

        messages.append({"role": "assistant",
                         "content": f"""Last response: {last_response}.\nUser replied: {user_text}.\n Respond like {person}. {philosophy_text} Be concise. {{"response": XXX, "cart_items": [X, Y, Z]}}. The JSON object: \n\n"""})

    # base64_image = encode_image(image_path)
    client = OpenAI()
    response = client.chat.completions.create(
        # model="gpt-4-vision-preview",
        response_format={"type": "json_object"},
        model="gpt-3.5-turbo-1106",
        messages=messages,
        max_tokens=300,
    )

    print(response)
    res = json.loads(response.choices[0].message.content)
    user_response = res['response']
    cart_items = res.get('cart_items', ['error'])
    print(cart_items)
    last_response = json.dumps(res)

    # Write this to a file called 'cart.txt'
    with open("cart.txt", "w") as f:
        f.write("\n".join(cart_items))

    return user_response


class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")


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
            if duration and elapsed_time > duration:
                break

            frames.write(buffer)

    # print("broke out of thread")
    frame_data = frames.getvalue()
    frames.close()
    return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)


def get_user_transcription():
    init_rec = sr.Recognizer()
    print("Please speak: ")
    with sr.Microphone() as source:
        audio_data = record(source)
        print("Recognizing your text.............")
        text = init_rec.recognize_google(audio_data)
        return str(text)


def say_eleven_labs(text):
    # print("Generating voice...")
    audio = elabs.generate(voice=obama, text=text)
    # print("Done...")
    data = sf.read(io.BytesIO(audio))
    sd.play(*data)

    while True:
        if os.path.isdir("./stopped"):
            sd.stop()
            break
        time.sleep(1)


def reset_file():
    try:
        os.removedirs("./stopped")
    except Exception as e:
        pass


reset_file()

print("Talk to obama")
reset_file()

initial_response = ask_gpt(user_text=None)
reset_file()
say_eleven_labs(initial_response)

while True:

    try:
        reset_file()
        user_inputted_text = get_user_transcription()
        reset_file()

        print("You said: ", user_inputted_text)
        # print("Asking GPT!")

        text = ask_gpt(user_text=user_inputted_text)

        reset_file()
        say_eleven_labs(text)
        # x = input()
        # time.sleep(delay)
    except Exception as e:
        print("ERROR", e)
        continue
