"use client";
import { useState, useEffect } from "react";
import ItemPreView from "./ItemPreView";
import { FilterItemSortField, FilterSortOrder, Item } from "../interfaces/Item";
import { ActionMeta, MultiValue } from "react-select";
import { OptionType } from "../interfaces/Order";
import dynamic from "next/dynamic";
const Select = dynamic(() => import("react-select"), { ssr: false });

export default function SelectedItems({
  items,
  tags,
  effects,
}: {
  items: Item[];
  tags: string[];
  effects: string[];
}) {
  const maxPrice = Math.max(...items.map((item) => item.gold.base));
  const minPrice = Math.min(...items.map((item) => item.gold.base));
  const [filterItemNames, setFilterItemName] = useState<string[]>([]);
  const [filterMinPrice, setFilterMinPrice] = useState<number>(minPrice);
  const [filterMaxPrice, setFilterMaxPrice] = useState<number>(maxPrice);
  const [filterTagNames, setFilterTagNames] = useState<string[]>([]);
  const [filterEffectNames, setFilterEffectNames] = useState<string[]>([]);
  const [sortField, setSortField] = useState<FilterItemSortField>(
    FilterItemSortField.NAME,
  );
  const [sortOrder, setSortOrder] = useState<FilterSortOrder>(
    FilterSortOrder.DESC,
  );
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  const itemNameSelectOptions: OptionType[] = items.map((item) => ({
    value: item.name,
    label: item.name,
  }));
  const itemTagSelectOptions: OptionType[] = tags.map((tag: string) => ({
    value: tag,
    label: tag,
  }));
  const itemEffectSelectOptions: OptionType[] = effects.map((tag: string) => ({
    value: tag,
    label: tag,
  }));

  function handleItemNameFilterChange(
    selectedNames: MultiValue<OptionType>,
    _actionMeta: ActionMeta<OptionType>,
  ) {
    const itemNames = selectedNames.map((option) => option.value);
    setFilterItemName(itemNames);
    setCurrentPage(1);
  }
  function handleTagFilterChange(
    selectedNames: MultiValue<OptionType>,
    _actionMeta: ActionMeta<OptionType>,
  ) {
    const tagNames = selectedNames.map((option) => option.value);
    setFilterTagNames(tagNames);
    setCurrentPage(1);
  }
  function handleEffectFilterChange(
    selectedNames: MultiValue<OptionType>,
    _actionMeta: ActionMeta<OptionType>,
  ) {
    const effectNames = selectedNames.map((option) => option.value);
    setFilterEffectNames(effectNames);
    setCurrentPage(1);
  }
  const handleSortItemFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortField(e.target.value as FilterItemSortField);
    setCurrentPage(1);
  };

  const handleSortOrderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortOrder(e.target.value as FilterSortOrder);
    setCurrentPage(1);
  };

  function checkItemsAttributeInFilterList(itemsAttribute: string[], filterStrings: string[]) {
    if (filterStrings.length == 0) {
      return true;
    } else {
      return itemsAttribute.some((attr: string) => filterStrings.includes(attr));
    }
  }

  const filteredItems: Item[] = items.filter((item: Item) => (
    (checkItemsAttributeInFilterList(item.effects.map(e => e.name), filterEffectNames)) &&
    (checkItemsAttributeInFilterList(item.tags, filterTagNames)) &&
    (filterItemNames.length == 0 ? true : filterItemNames.includes(item.name)) &&
    (item.gold.base <= filterMaxPrice && item.gold.base >= filterMinPrice)
  ))
    .sort((a, b) => {
      let comparison: number = 0;
      switch (sortField) {
        case FilterItemSortField.PRICE:
          comparison = a.gold.base - b.gold.base;
          break;
        case FilterItemSortField.NAME:
          comparison = a.name.localeCompare(b.name);
          break;
        default:
          break;
      }
      return sortOrder === FilterSortOrder.DESC ? -comparison : comparison;
    });



  //For example 20 items on pages of six need 4 pages ceil(20/6) = 4
  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  //Takes items from the list based on the page
  const paginatedItems = filteredItems.slice(
    startIndex,
    startIndex + itemsPerPage,
  );

  //Check if reset when changing items, pages o current page
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(1);
    }
  }, [filteredItems, totalPages, currentPage]);

  return (
    <div className="grid grid-cols-2 grid-cols-[13%_80%] gap-4 h-full">
      <aside
        className="p-4 flex flex-col shadow-lg overflow-y-auto h-screen 
        bg-[var(--white)] text-[var(--black)] sticky top-0"
      >
        <h2 className="text-lg font-bold mb-2">Sort By</h2>
        <div className="flex flex-col gap-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="sortField"
              value={FilterItemSortField.PRICE}
              checked={sortField === FilterItemSortField.PRICE}
              onChange={handleSortItemFieldChange}
            />
            <span className="ml-2">Price</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="sortField"
              value={FilterItemSortField.NAME}
              checked={sortField === FilterItemSortField.NAME}
              onChange={handleSortItemFieldChange}
            />
            <span className="ml-2">Name</span>
          </label>
        </div>

        <h2 className="text-lg font-bold mt-4 mb-2">Sort Order</h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="sortOrder"
              value="asc"
              checked={sortOrder === "asc"}
              onChange={handleSortOrderChange}
            />
            <span className="ml-2">Ascending</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="sortOrder"
              value="desc"
              checked={sortOrder === "desc"}
              onChange={handleSortOrderChange}
            />
            <span className="ml-2">Descending</span>
          </label>
        </div>


        <div className="mt-4">
          <label htmlFor="minPrice" className="block font-bold mb-1">
            Min Price:
          </label>
          <input
            id="minPrice"
            type="number"
            value={filterMinPrice}
            onChange={(e) => setFilterMinPrice(Number(e.target.value))}
            className="w-full border rounded px-2 py-1"
          />
        </div>
        <div>
          <label htmlFor="maxPrice" className="block font-bold mb-1">
            Max Price:
          </label>
          <input
            id="maxPrice"
            type="number"
            value={filterMaxPrice}
            onChange={(e) => setFilterMaxPrice(Number(e.target.value))}
            className="w-full border rounded px-2 py-1"
          />
        </div>

        <h2 className="font-bold mb-2 my-2">Items</h2>
        <Select
          isMulti
          options={itemNameSelectOptions}
          onChange={handleItemNameFilterChange}
          placeholder="Select item names..."
        />

        <h2 className="font-bold mb-2 my-2">Tags</h2>
        <Select
          isMulti
          options={itemTagSelectOptions}
          onChange={handleTagFilterChange}
          placeholder="Select tags..."
        />

        <h2 className="font-bold mb-2 my-2">Effects</h2>
        <Select
          isMulti
          options={itemEffectSelectOptions}
          onChange={handleEffectFilterChange}
          placeholder="Select effects..."
        />

      </aside>

      <div className="p-4 ml-8 flex items-center flex-col gap-y-2">
        {paginatedItems.map((item, index) => (
          <ItemPreView key={index} item={item} />
        ))}

        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-4">
            <button
              onClick={() => {
                setCurrentPage((prev) => Math.max(prev - 1, 1));
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => {
                setCurrentPage((prev) => Math.min(prev + 1, totalPages));
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
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
