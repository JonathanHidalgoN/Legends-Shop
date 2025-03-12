"use client";
import { useState, useEffect } from "react";
import ItemPreView from "./ItemPreView";
import { Item } from "../interfaces/Item";

export default function SelectedItems({ items, tags }: { items: Item[]; tags: string[] }) {
  const maxPrice = Math.max(...items.map(item => item.gold.base));
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [price, setPrice] = useState<number>(maxPrice);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  //Check if add the tag or remove it
  const handleTagToggle = (tag: string) => {
    setSelectedTags((tagList) =>
      tagList.includes(tag)
        ? tagList.filter((tagToRemove) => tagToRemove !== tag)
        : [...tagList, tag]
    );
    //Reset the page
    setCurrentPage(1);
  };

  const filteredItems: Item[] = items
    .filter((item) => {
      if (selectedTags.length === 0) return true;
      return selectedTags.every((tag) => item.tags.includes(tag));
    })
    .filter((item) => item.gold.base <= price);

  //For example 20 items on pages of six need 4 pages ceil(20/6) = 4 
  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  //Takes items from the list based on the page
  const paginatedItems = filteredItems.slice(startIndex, startIndex + itemsPerPage);

  //Check if reset when changing items, pages o current page
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(1);
    }
  }, [filteredItems, totalPages, currentPage]);

  return (
    <div className="grid grid-cols-2 grid-cols-[13%_auto] gap-4 h-full">
      <aside className="p-2 flex flex-col shadow-lg bg-[var(--white)] text-[var(--black)]">
        <div className="mb-6">
          <h2 className="font-bold mb-2">Price</h2>
          <div className="flex items-center">
            <span className="mr-2">0</span>
            <input
              type="range"
              min="0"
              max={maxPrice}
              value={price}
              onChange={(e) => {
                setPrice(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="flex-grow"
            />
            <span className="ml-2">{price}</span>
          </div>
        </div>

        <div className="flex-grow overflow-y-auto custom-scrollbar">
          <ul className="space-y-2">
            {tags.map((tag, index) => (
              <li
                key={index}
                className="flex items-center p-2 rounded hover:bg-gray-200 transition-colors"
              >
                <input
                  type="checkbox"
                  className="w-5 h-5 mr-2 hover:cursor-pointer"
                  onChange={() => handleTagToggle(tag)}
                  checked={selectedTags.includes(tag)}
                />
                <span className="hover:text-orange-500 transition-colors">{tag}</span>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <div className="p-4 flex flex-col gap-y-2">
        {paginatedItems.map((item, index) => (
          <ItemPreView key={index} item={item} />
        ))}

        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-4">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
