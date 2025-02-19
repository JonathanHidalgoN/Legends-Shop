"use client";
import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Item } from "../interfaces/Item";
import { kanit, sigmar } from "../fonts";
import DescriptionTextMapper from "./DescriptionTextMapper";

export default function ItemPreView({ item }: { item: Item }) {
  const [isHovered, setIsHovered] = useState(false);
  const targetLink = `/items/${item.name}`;

  return (
    <div className="m-6 relative border border-[var(--yellow)]">
      <Link href={targetLink}>
        <div
          className="block cursor-pointer"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {/* The square container with the item image */}
          <div className="relative w-40 h-40 rounded overflow-hidden shadow-md">
            <Image
              src={item.img}
              alt={item.name}
              fill
              sizes="(max-width: 768px) 25vw, (max-width: 1200px) 25vw, 25vw"
              quality={100}
            />
          </div>

          {/* Price below the image */}
          <div className="mt-2 text-center">
            <span className={`text-xl text-[var(--yellow)] ${kanit.className}`}>
              {item.gold.base} g</span>
          </div>
        </div>
      </Link>

      {isHovered && (
        <div
          className="border border-black absolute left-full w-80 z-10 p-4 rounded bg-[var(--white2)] transition-opacity duration-300"
          style={{ top: 0 }}
        >
          {/* Item Name at the top of the hover panel */}
          <div className="mb-2">
            <span className={`text-[var(--orange)] text-xl ${sigmar.className}`}>
              {item.name}</span>
          </div>

          {/* Gold Information */}
          <div className="text-[var(--extra)]">
            <span className="font-bold text-[var(--black)]">Cost: </span>
            <span className={`text-[var(--yellow)] text-xl ${kanit.className}`}>
              {item.gold.base} g
            </span>
          </div>

          {/* Stats List */}
          {item.stats && item.stats.length > 0 && (
            <div className="mt-2">
              <span className="font-bold text-[var(--black)]">Stats:</span>
              <ul className="list-disc list-inside">
                {item.stats.map((stat, index) => (
                  <li key={index} className="text-[var(--black)]">
                    <span className={`text-[var(--orange)] ${kanit.className}`}>
                      {stat.value}
                    </span>
                    {stat.kind === 0 ? "" : "%"} {stat.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Effects List */}
          {item.effects && item.effects.length > 0 && (
            <div className="mt-2">
              <span className="font-bold text-black">Effects:</span>
              <ul className="list-disc list-inside">
                {item.effects.map((effect, index) => (
                  <li key={index} className="text-[var(--black)]">
                    <span className={`text-[var(--pink1)] ${kanit.className}`}>
                      {effect.value}{' '}
                    </span>
                    {effect.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Description */}
          <div className="mt-2 text-[var(--black)]">
            <span className="font-bold">Description:</span>
            <DescriptionTextMapper description={item.description} />
          </div>
        </div>
      )}
    </div>
  );
}
