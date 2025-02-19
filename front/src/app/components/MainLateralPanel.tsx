"use client";
import { useState } from "react";

export default function MainLateralPanel({ maxPrice, tags }: { maxPrice: number, tags: string[] }) {
  const [price, setPrice] = useState(0);
  return (
    <aside
      className="w-64 p-2 h-full flex flex-col shadow-lg"
      style={{
        backgroundColor: "var(--white)",
        color: "var(--black)",
      }}
    >
      <div className="mb-6">
        <h2 className="font-bold mb-2">Price</h2>
        <div className="flex items-center">
          <span className="mr-2">0</span>
          <input
            type="range"
            min="0"
            max={100}
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
            className="flex-grow"
          />
          <span className="ml-2">{price}</span>
        </div>
      </div>

      <div className="flex-grow overflow-y-auto custom-scrollbar">
        <ul className="space-y-2">
          {tags.map((tag, index) => (
            <li key={index} className="flex items-center">
              <input
                type="checkbox"
                className="w-5 h-5 mr-2"
              />
              <span>{tag}</span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
