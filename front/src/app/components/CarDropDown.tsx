"use client";

import { Item } from "../interfaces/Item";
import Image from "next/image";
import { useCarContext } from "./CarContext";

type ItemSummary = {
  count: number;
  total: number;
  itemSample: Item;
};

export default function CarDropDown({ tiny }: { tiny: boolean }) {
  const {
    carItems,
    deleteOneItemFromCar,
    deleteAllItemFromCar,
    addOneItemToCar,
    getTotalCost,
  } = useCarContext();
  const itemCount: Record<string, ItemSummary> = {};
  const totalCost: number = getTotalCost();

  carItems.forEach((item: Item) => {
    if (item.name in itemCount) {
      itemCount[item.name].count += 1;
      itemCount[item.name].total += item.gold.base;
    } else {
      itemCount[item.name] = {
        count: 1,
        total: item.gold.base,
        itemSample: item,
      };
    }
  });

  return (
    <div>
      <div className="space-y-4">
        {Object.values(itemCount).map((summary, index) => (
          <div key={index} className="flex items-center justify-between p-2">
            <div className="flex items-center">
              <button
                onClick={() => deleteAllItemFromCar(summary.itemSample)}
                className="text-red-500 text-m focus:outline-none"
              >
                &times;
              </button>
              <div className="relative w-10 h-10 ml-4 mr-2">
                <Image
                  src={summary.itemSample.img}
                  alt={summary.itemSample.name}
                  fill
                  className="object-cover rounded"
                />
              </div>
              <div>
                <p className="font-semibold text-sm">
                  {summary.itemSample.name}
                </p>
                <p className="text-xs text-gray-600">
                  {summary.itemSample.gold.base} g
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => addOneItemToCar(summary.itemSample)}
                className={
                  !tiny
                    ? `w-12 bg-green-500 text-white py-2 rounded 
                           hover:bg-green-700 transition-colors`
                    : `w-6 bg-green-500 text-white py-2 rounded 
                           hover:bg-green-700 transition-colors`
                }
              >
                +
              </button>
              <span className="text-sm px-2">{summary.count}</span>
              <button
                onClick={() => deleteOneItemFromCar(summary.itemSample)}
                className={
                  !tiny
                    ? `w-12 bg-red-500 text-white py-2 rounded 
                           hover:bg-red-700 transition-colors`
                    : `w-6 bg-red-500 text-white py-2 rounded 
                           hover:bg-red-700 transition-colors`
                }
              >
                -
              </button>
              <span className="text-base font-bold whitespace-nowrap">
                {summary.total} g
              </span>
            </div>
          </div>
        ))}
      </div>

      {!tiny && (
        <div className="mt-6 border-t pt-4">
          <div className="flex justify-between mb-4">
            <span className="font-bold">Total:</span>
            <span className="font-bold text-[var(--yellow)]">
              {totalCost} g
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
