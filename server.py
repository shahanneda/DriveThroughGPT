import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/cart")
async def read_cart():
    with open("cart.txt", "r") as f:
        cart_items = f.read().splitlines()
        print(cart_items)

    return {"items": cart_items}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
