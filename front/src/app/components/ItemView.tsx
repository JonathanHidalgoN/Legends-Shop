"use client";

import Image from "next/image";
import { Item } from "../interfaces/Item";
import DescriptionTextMapper from "./DescriptionTextMapper";
import AddToCarButton from "./AddToCarButton";
import { useStaticData } from "./StaticDataContext";

export default function ItemView({ itemName }: { itemName: string }) {
  const { items } = useStaticData();
  const item: Item | undefined = items.find((i) => i.name === itemName);
  if (!item) return <div>Item not found</div>;

  return (
    <div className="max-w-5xl mx-auto p-4 flex flex-col md:flex-row">
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

      <div className="md:w-1/2 md:ml-6 mt-4 md:mt-0">
        <h1 className="text-4xl font-bold text-[var(--orange)]">{item.name}</h1>
        <p className="mt-2 text-2xl text-[var(--yellow)]">{item.gold.base} g</p>

        <div className="mt-4 text-gray-700">
          <span className="font-bold">Description: </span>
          <DescriptionTextMapper
            description={item.description}
            maxLen={999999}
          />
        </div>

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

        <AddToCarButton item={item} />
      </div>
    </div>
  );
}
