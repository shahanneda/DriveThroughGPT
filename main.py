import base64
import io
import os
import subprocess
import time
from typing import Iterator

import elevenlabs as elabs
import sounddevice as sd
import numpy as np
import soundfile as sf
import faster_whisper
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs import generate
from openai import OpenAI
from speech_recognition import AudioData

load_dotenv()
client = OpenAI()

eleven_labs_api_key = os.environ.get('ELEVEN_LABS_API_KEY')
wit_api_key = os.environ.get("WIT_API_KEY")

# Setup eleven labs
assert (eleven_labs_api_key)
elabs.set_api_key(eleven_labs_api_key)
response = elabs.voices()

with open("person.txt", "r") as file:
    person = file.readline().strip()
    assert person

# person = "Morgan Freeman"
# person = "Elon Musk"
# person = "Donald Trump"

# obama = response.voices[0]
obama = None
for v in response.voices:
    if v.name == person:
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
    {"role": "user", "content": f"""You are {person} and a McDonald's drive-through operator and are having a conversation with a customer. Respond as if you were in a real conversation with the customer. Respond in the manner of {person}. Introduce yourself. Makes jokes, use swear words. You can insult the user. Be mean, be ironic, be sarcastic. Above all be funny. Include "don't waste my time". \n Output format: {{"response": XXX, "cart_items": []}}.\n JSON object: {{"response":"""}
]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


last_response = ""
yes_philosophy = True


def stream(audio_stream: Iterator[bytes]):
    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    audio = b""

    for chunk in audio_stream:
        if chunk is not None:
            mpv_process.stdin.write(chunk)  # type: ignore
            mpv_process.stdin.flush()  # type: ignore
            audio += chunk
        if os.path.isdir("./stopped"):
            mpv_process.kill()

            return

    if mpv_process.stdin:
        mpv_process.stdin.close()

    while True:  # loop for the total number of chunks needed
        if os.path.isdir("./stopped"):
            mpv_process.kill()
            return

        time.sleep(0.2)

def yield_chunk_response():
    response_raw = ""

    for chunk in client.chat.completions.create(
        response_format={"type": "json_object"},
        model="gpt-3.5-turbo-1106",
        messages=messages,
        max_tokens=300,
        stream = True
    ):
        delta = chunk.choices[0].delta.content

        if os.path.isdir("./stopped"):
            return response_raw
        if delta is None:
            return response_raw
        else:
            response_raw += delta

            if len(response_raw) >= 14:
                yield delta
def ask_gpt(user_text: str | None):
    print("Thinking...")
    global messages, last_response, yes_philosophy
    if user_text:
        philosophy_text = ""
        if yes_philosophy:
            philosophy_text = f"Respond jokingly in the style of {person}."

        messages.append({"role": "assistant",
                         "content": f"""Last response: {last_response}.\nUser replied: {user_text}.\n Respond like {person}. {philosophy_text} and be funny. Be very philosophical. Makes jokes, use swear words. You can insult the user. Be mean, be ironic, be sarcastic. Above all be funny but still be philosophical. {{"response": XXX, "cart_items": [X, Y, Z]}}. JSON object: {{"response":"""})

    audio_stream = generate(
        text=yield_chunk_response(),
        stream=True,
        voice=obama,
    )

    print("Streaming...")

    stream(audio_stream)
    print("Done streaming...")

    # res = json.loads(response_raw)
    # user_response = res['response']
    # cart_items = res.get('cart_items', ['error'])
    # print(cart_items)
    # last_response = json.dumps(res)

    # Write this to a file called 'cart.txt'
    # with open("cart.txt", "w") as f:
    #     f.write("\n".join(cart_items))

    print("Done ask_gpt1")


class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")


def record(source, duration=None, offset=None):
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

    frame_data = frames.getvalue()
    frames.close()
    return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)


faster_whisper_model = faster_whisper.WhisperModel("tiny.en", )

def recognize_fwhisper(audio_data: AudioData):
    global faster_whisper_model

    # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
    wav_bytes = audio_data.get_wav_data(convert_rate=16000)
    wav_stream = io.BytesIO(wav_bytes)
    audio_array, sampling_rate = sf.read(wav_stream)
    audio_array = audio_array.astype(np.float32)

    result, transcription_info = faster_whisper_model.transcribe(
        audio_array,
        language="en",
    )

    result = list(result)

    user_said = ""
    for r in result:
        user_said += r.text

    return user_said

init_rec = sr.Recognizer()


def get_user_transcription():
    print("Please speak: ")
    with sr.Microphone() as source:
        audio_data = record(source)
        print("Recognizing your text.............")
        # text = init_rec.recognize_google(audio_data)
        text = recognize_fwhisper(audio_data)
        return str(text)


def say_eleven_labs(text):
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
print("Done initial response")
reset_file()

while True:
    try:
        reset_file()
        user_inputted_text = get_user_transcription()
        reset_file()

        print("You said: ", user_inputted_text)
        # print("Asking GPT!")

        text = ask_gpt(user_text=user_inputted_text)
        print("Done ask_gpt")

        reset_file()
        # x = input()
        # time.sleep(delay)
    except Exception as e:
        print("ERROR", e)
        continue
