"use client";

import Link from "next/link";
import { Item } from "../interfaces/Item";
import DescriptionTextMapper from "./DescriptionTextMapper";
import AddToCarButton from "./AddToCarButton";
import { useRouter } from "next/navigation";
import Image from "next/image";
import EpicLegendMap from "./EpicLegendMap";

export default function ItemPreView({ item }: { item: Item }) {
  const targetLink = `/items/${item.name}`;
  const router = useRouter();

  const handleCardClick = () => {
    router.push(targetLink);
  };

  return (
    <div
      onClick={handleCardClick}
      className="flex flex-col w-full md:flex-row items-start p-8 border border-black items-center rounded-lg shadow-sm my-4 hover:shadow-xl hover:scale-105 hover:border-gold hover:bg-gray-50 transition-all duration-300 ease-in-out cursor-pointer"
    >
      <div className="flex-shrink-0 ">
        <Link href={targetLink}>
          <div className="relative w-32 h-32 md:w-40 md:h-40">
            <Image
              src={item.img}
              alt={item.name}
              fill
              className="object-cover rounded hover:opacity-90 transition-opacity"
            />
          </div>
        </Link>
      </div>

      <div className="flex-1 md:ml-4 md:mt-0">
        <h3 className="text-xl font-bold text-[var(--black)]">{item.name}</h3>
        <div className="m-2">
          <EpicLegendMap itemName={item.name} />
        </div>
        <DescriptionTextMapper description={item.description} />
        {item.tags.length > 0 && (
          <div className="mt-3">
            <span className="text-sm font-medium text-gray-700">Tags: </span>
            {item.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-block bg-orange-200 text-black text-xs px-2 py-1 rounded mr-2 mt-1"
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
                className="inline-block bg-[var(--pink2)] text-black text-xs px-2 py-1 rounded mr-2 mt-1"
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
        <div className="mt-2" onClick={(e) => e.stopPropagation()}>
          <AddToCarButton item={item} />
        </div>
      </div>
    </div>
  );
}
