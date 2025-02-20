"use client";

import Image from "next/image";
import { Item } from "../interfaces/Item";
import DescriptionTextMapper from "./DescriptionTextMapper";
import { useStaticData } from "./StaticDataContext";

export default function ItemView({ itemName }: { itemName: string }) {
  const { items } = useStaticData();
  const item: Item | undefined = items.find((i) => i.name === itemName);
  if (!item) return <div>Item not found</div>;

  return (
    <div className="max-w-5xl mx-auto p-4 flex flex-col md:flex-row">
      {/* Image Section */}
      <div className="md:w-1/2">
        <div className="relative w-full h-96 rounded overflow-hidden shadow-lg">
          <Image
            src={item.img}
            alt={item.name}
            fill
            style={{ objectFit: "cover" }}
            quality={100}
          />
        </div>
      </div>

      {/* Details Section */}
      <div className="md:w-1/2 md:ml-6 mt-4 md:mt-0">
        {/* Item Title */}
        <h1 className="text-4xl font-bold text-[var(--orange)]">
          {item.name}
        </h1>
        {/* Price */}
        <p className="mt-2 text-2xl text-[var(--yellow)]">
          {item.gold.base} g
        </p>

        {/* Description */}
        <div className="mt-4 text-gray-700">
          <span className="font-bold">Description: </span>
          <DescriptionTextMapper description={item.description} />
        </div>

        {/* Stats */}
        {item.stats && item.stats.length > 0 && (
          <div className="mt-4">
            <span className="font-bold">Stats:</span>
            <ul className="list-disc list-inside">
              {item.stats.map((stat, index) => (
                <li key={index}>
                  <span className="text-[var(--orange)]">
                    {stat.value}
                    {stat.kind === 0 ? "" : "%"}
                  </span>{" "}
                  {stat.name}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Effects */}
        {item.effects && item.effects.length > 0 && (
          <div className="mt-4">
            <span className="font-bold">Effects:</span>
            <ul className="list-disc list-inside">
              {item.effects.map((effect, index) => (
                <li key={index}>
                  <span className="text-[var(--pink1)]">{effect.value}</span>{" "}
                  {effect.name}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Buy Button */}
        <button
          className="mt-6 bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition-colors"
          onClick={() => alert("Buy functionality coming soon!")}
        >
          Buy Now
        </button>

      </div>
    </div>
  );
}
