"use client";

import axios from "axios";
import { useEffect, useState } from "react";

const getCart = async () => {
  const { data } = await axios.get("http://localhost:8000/cart");
  return data.items;
};

export default function Home() {
  const [cart, setCart] = useState<string[]>([]);

  // Poll every second for the cart
  useEffect(() => {
    const interval = setInterval(async () => {
      const cart = await getCart();
      setCart(cart);
    }, 1000);
    return () => clearInterval(interval);
  });

  return (
    <main>
      Cart:
      <div>
        {cart.map((item) => (
          <div key={item}>{item}</div>
        ))}
      </div>
    </main>
  );
}
