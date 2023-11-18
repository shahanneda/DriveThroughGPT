import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/cart")
async def read_cart():
    with open("cart.txt", "r") as f:
        cart_items = f.read().splitlines()
        print(cart_items)

    return {"items": cart_items}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
