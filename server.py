import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google_images_search import GoogleImagesSearch

load_dotenv()

google_api_key = os.environ.get('GOOGLE_API_KEY')
google_context = os.environ.get("GOOGLE_CX")

gis = GoogleImagesSearch(google_api_key, google_context)

app = FastAPI()

origins = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue
    "http://localhost:4200",  # Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


cached_images = {}


def get_image(name, extra_prompt=""):
    if name in cached_images:
        return cached_images[name]

    _search_params = {
        'q': name + extra_prompt,
        'num': 1,
    }
    gis.search(search_params=_search_params)
    for image in gis.results():
        cached_images[name] = image.url
        return image.url


def get_person():
    with open("person.txt", "r") as file:
        person = file.readline().strip()
        assert person
        return person


@app.get("/person")
async def read_cart():
    person = get_person()
    url = get_image(person + " wearing a headset")
    return {"name": get_person(), "url": url}

@app.get("/cart")
async def read_cart():
    with open("cart.txt", "r") as f:
        cart_items = f.read().splitlines()
        out = []
        for item in cart_items:
            url = get_image(item)
            out.append({"name": item, "url": url})

    return {"items": out}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
