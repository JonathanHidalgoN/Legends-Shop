"use client";

import Link from "next/link";
import { Item } from "../interfaces/Item";
import DescriptionTextMapper from "./DescriptionTextMapper";
import AddToCarButton from "./AddToCarButton";

export default function ItemPreView({ item }: { item: Item }) {
  const targetLink = `/items/${item.name}`;

  return (
    <div className="flex flex-col md:flex-row items-start p-4 border rounded-lg shadow-sm my-4 hover:shadow-md transition-shadow">
      <div className="flex-shrink-0">
        <Link href={targetLink}>
          <img
            src={item.img}
            alt={item.name}
            className="w-32 h-32 md:w-40 md:h-40 object-cover rounded hover:opacity-90 transition-opacity"
          />
        </Link>
      </div>

      <div className="flex-1 md:ml-4 mt-4 md:mt-0">
        <h3 className={`text-xl font-bold text-[var(--black)]`}>{item.name}</h3>
        <div className="mt-2">
          <DescriptionTextMapper description={item.description} maxLen={700} />
        </div>

        {item.tags.length > 0 && (
          <div className="mt-3">
            <span className="text-sm font-medium text-gray-700">Tags: </span>
            {item.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2 mt-1"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {item.effects.length > 0 && (
          <div className="mt-3">
            <span className="text-sm font-medium text-gray-700">Effects: </span>
            {item.effects.map((effect, index) => (
              <span
                key={index}
                className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded mr-2 mt-1"
              >
                {effect.name} ({effect.value})
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 md:mt-0 md:ml-4 flex-shrink-0 flex flex-col items-end">
        <div className="text-right">
          <span className="text-2xl font-bold text-orange-600">
            ${item.gold.total}
          </span>
        </div>
        <div className="mt-2">
          <AddToCarButton item={item} />
        </div>
      </div>
    </div>
  );
}
