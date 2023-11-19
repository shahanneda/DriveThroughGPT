"use client";

import axios from "axios";
import { useEffect, useState } from "react";

const getCart = async () => {
  const { data } = await axios.get("http://localhost:8000/cart");
  return data.items;
};

const getPerson = async () => {
  const { data } = await axios.get("http://localhost:8000/person");
  return data;
};

interface Item {
  name: string;
  url: string;
}

export default function Home() {
  const [cart, setCart] = useState<string[]>([]);
  const [person, setPerson] = useState<Item>();

  // Poll every second for the cart
  useEffect(() => {
    const interval = setInterval(async () => {
      const cart = await getCart();
      setCart(cart);
    }, 1000);
    return () => clearInterval(interval);
  });
  useEffect(() => {
    (async () => {
      console.log("getting person");
      const person = await getPerson();
      console.log(person);
      setPerson(person);
    })();
  }, []);

  const Card = ({ item }: { item: Item }) => {
    return (
      <div className="border border-slate-500 rounded-lg p-4 w-40">
        {item.name}
        <img src={item.url} alt="item" />
      </div>
    );
  };

  return (
    <main>
      <div className="text-center mt-8 items-center">
        <div className="mt-8 space-y-2 self-center flex flex-col items-center">
          {person ? <img src={person.url} alt="item" width={250} /> : undefined}
        </div>

        <h1 className="font-bold text-xl mt-2">Cart:</h1>
        <div className="mt-8 space-y-2 self-center flex flex-col items-center">
          {cart.map((item) => (
            <Card key={item} item={item} />
          ))}
        </div>
      </div>
    </main>
  );
}
