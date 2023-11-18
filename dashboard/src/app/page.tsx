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

  const Card = ({ item }: { item: string }) => {
    return (
      <div className="border border-slate-500 rounded-lg inline-block p-4">
        {item}
      </div>
    );
  };

  return (
    <main>
      <div className="text-center mt-8">
        <h1 className="font-bold text-xl">Cart:</h1>
        <div className="mt-4">
          {cart.map((item) => (
            <Card key={item} item={item} />
          ))}
        </div>
      </div>
    </main>
  );
}
