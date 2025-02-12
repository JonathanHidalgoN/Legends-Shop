"use client"
// components/ItemPreView.jsx
import Link from "next/link";
import Image from "next/image";

export default function ItemPreView({
  item,
  linkHref = "/",
}) {
  const targetLink = linkHref || `/items/${item.name}`;

  return (
    <Link href={targetLink}>
      {/* Set the container as relative so that the detail panel can be absolutely positioned */}
      <div className="m-6 group block relative cursor-pointer">
        {/* The square container with the item image */}
        <div
          className={`relative w-64 h-64 rounded overflow-hidden shadow-md`}
        >
          <Image
            src={item.img}
            alt={item.name}
            layout="fill"
            objectFit="cover"
          />
          {/* Overlay for the item name */}
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-2">
            <p className="text-white text-center font-bold">{item.name}</p>
          </div>
        </div>

        {/* Detail panel which is hidden by default and appears on hover */}
        <div
          className={`border border-black absolute left-0 w-full z-10 p-4 rounded bg-[var(--white)] opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
          style={{ top: "100%" }}
        >
          {/* Gold Information */}
          <div className="text-[var(--extra)]">
            <span className="font-bold text-[var(--black)]">Cost:</span> {item.gold.base}
          </div>
          {/* Stats List */}
          {item.stats && item.stats.length > 0 && (
            <div className="mt-2">
              <span className="font-bold text-[var(--black)]">Stats:</span>
              <ul className="list-disc list-inside">
                {item.stats.map((stat, index) => (
                  <li key={index} className="text-[var(--extra)]">
                    {stat.value}{stat.type === 0 ? "" : "%"} {stat.name}
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
                  <li key={index} className="text-[var(--extra)]">
                    {effect.value} {effect.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Description */}
          <div className="mt-2 text-[var(--extra)]">
            <span className="font-bold text-[var(--black)]">Description:</span>
            {item.description}
          </div>
        </div>
      </div>
    </Link>
  );
}
