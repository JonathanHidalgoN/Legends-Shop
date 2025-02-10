"use client"
// components/ItemPreView.jsx
import Link from "next/link";
import Image from "next/image";

export default function ItemPreView({
  item,
  squareBg = "bg-gray-200",
  squareText = "text-black",
  detailBg = "bg-white",
  detailText = "text-gray-800",
  statText = "text-blue-500",
  effectText = "text-green-500",
  linkHref = "/",
}) {
  const targetLink = linkHref || `/items/${item.name}`;

  return (
    <Link href={targetLink}>
      {/* Set the container as relative so that the detail panel can be absolutely positioned */}
      <div className="group block relative cursor-pointer">
        {/* The square container with the item image */}
        <div
          className={`relative w-64 h-64 ${squareBg} ${squareText} rounded overflow-hidden shadow-md`}
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
          className={`absolute left-0 w-full z-10 p-4 rounded ${detailBg} ${detailText} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
          style={{ top: "100%" }}
        >
          {/* Gold Information */}
          <div>
            <span className="font-bold">Base Gold:</span> {item.gold.base}
          </div>

          {/* Stats List */}
          {item.stats && item.stats.length > 0 && (
            <div className="mt-2">
              <span className="font-bold">Stats:</span>
              <ul className="list-disc list-inside">
                {item.stats.map((stat, index) => (
                  <li key={index} className={statText}>
                    {stat.name}: {stat.value} (
                    {stat.type === 0 ? "Flat" : "Percentage"})
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Effects List */}
          {item.effects && item.effects.length > 0 && (
            <div className="mt-2">
              <span className="font-bold">Effects:</span>
              <ul className="list-disc list-inside">
                {item.effects.map((effect, index) => (
                  <li key={index} className={effectText}>
                    {effect.name}: {effect.value} (Effect {effect.type})
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Description */}
          <div className="mt-2">
            <span className="font-bold">Description:</span> {item.description}
          </div>
        </div>
      </div>
    </Link>
  );
}
