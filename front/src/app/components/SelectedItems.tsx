"use client"
import { useState } from "react"
import ItemPreView from "./ItemPreView"
import { Item } from "../interfaces/Item"

export default function SelectedItems({ items, tags }: { items: Item[]; tags: string[] }) {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [price, setPrice] = useState<number>(0);
  const handleTagToggle = (tag: string) => {
    setSelectedTags((tagList) =>
      tagList.includes(tag) ? tagList.filter((tagToRemove) => tagToRemove !== tag)
        : [...tagList, tag]
    );
  };
  const filteredItems: Item[] = items.filter((item) => {
    if (selectedTags.length === 0) return true;
    return selectedTags.every((tag) => item.tags.includes(tag));
  });
  const maxPrice = 10000;

  return (
    <div className="grid grid-cols-[15%_auto] h-full">
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
              max={maxPrice}
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
                  onChange={
                    //Using value from context
                    () => handleTagToggle(tag)
                  }
                  checked={selectedTags.includes(tag)}
                />
                <span>{tag}</span>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <div className="p-4 m-6 flex flex-wrap gap-x-10">
        {filteredItems.map((item, index) => (
          <ItemPreView key={index} item={item} />
        ))}
      </div>

    </div>
  );
}
