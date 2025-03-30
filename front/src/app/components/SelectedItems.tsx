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
  initialSearch,
}: {
  items: Item[];
  tags: string[];
  effects: string[];
  initialSearch?: string | null;
}) {
  const maxPrice = Math.max(...items.map((item) => item.gold.base));
  const minPrice = Math.min(...items.map((item) => item.gold.base));
  const [filterItemNames, setFilterItemName] = useState<string[]>(initialSearch ? [initialSearch] : []);
  const [filterMinPrice, setFilterMinPrice] = useState<number>(minPrice);
  const [filterMaxPrice, setFilterMaxPrice] = useState<number>(maxPrice);
  const [filterTagNames, setFilterTagNames] = useState<string[]>([]);
  const [filterEffectNames, setFilterEffectNames] = useState<string[]>([]);
  const [sortField, setSortField] = useState<FilterItemSortField>(
    FilterItemSortField.NAME,
  );
  const [sortOrder, setSortOrder] = useState<FilterSortOrder>(
    FilterSortOrder.ASC,
  );
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  // Update filterItemNames when initialSearch changes
  useEffect(() => {
    if (initialSearch) {
      setFilterItemName([initialSearch]);
    }
  }, [initialSearch]);

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
  const handleSortItemFieldChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setSortField(e.target.value as FilterItemSortField);
    setCurrentPage(1);
  };

  const handleSortOrderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortOrder(e.target.value as FilterSortOrder);
    setCurrentPage(1);
  };

  function checkItemsAttributeInFilterList(
    itemsAttribute: string[],
    filterStrings: string[],
  ) {
    if (filterStrings.length == 0) {
      return true;
    } else {
      return itemsAttribute.some((attr: string) =>
        filterStrings.includes(attr),
      );
    }
  }

  const filteredItems: Item[] = items
    .filter(
      (item: Item) =>
        checkItemsAttributeInFilterList(
          item.effects.map((e) => e.name),
          filterEffectNames,
        ) &&
        checkItemsAttributeInFilterList(item.tags, filterTagNames) &&
        (filterItemNames.length == 0
          ? true
          : filterItemNames.some(name => 
              item.name.toLowerCase().includes(name.toLowerCase())
            )) &&
        item.gold.base <= filterMaxPrice &&
        item.gold.base >= filterMinPrice,
    )
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
      <aside className="p-4 flex flex-col shadow-lg overflow-y-auto h-screen 
        bg-[var(--white)] text-[var(--black)] sticky top-0 rounded-lg">
        <div className="space-y-6">
          <div>
            <h2 className="text-lg text-[var(--orange)] font-bold mb-4">Sort By</h2>
            <div className="flex flex-col gap-3">
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterItemSortField.PRICE}
                  checked={sortField === FilterItemSortField.PRICE}
                  onChange={handleSortItemFieldChange}
                  className="mr-2"
                />
                <span>Price</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterItemSortField.NAME}
                  checked={sortField === FilterItemSortField.NAME}
                  onChange={handleSortItemFieldChange}
                  className="mr-2"
                />
                <span>Name</span>
              </label>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold mb-4 text-[var(--orange)]">Sort Order</h2>
            <div className="flex items-center gap-6">
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortOrder"
                  value="asc"
                  checked={sortOrder === "asc"}
                  onChange={handleSortOrderChange}
                  className="mr-2"
                />
                <span>Ascending</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortOrder"
                  value="desc"
                  checked={sortOrder === "desc"}
                  onChange={handleSortOrderChange}
                  className="mr-2"
                />
                <span>Descending</span>
              </label>
            </div>
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Price Range</h2>
            <div className="flex flex-col gap-3">
              <div>
                <label className="block font-semibold mb-1">Min Price</label>
                <input
                  id="minPrice"
                  type="number"
                  value={filterMinPrice}
                  onChange={(e) => setFilterMinPrice(Number(e.target.value))}
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">Max Price</label>
                <input
                  id="maxPrice"
                  type="number"
                  value={filterMaxPrice}
                  onChange={(e) => setFilterMaxPrice(Number(e.target.value))}
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                />
              </div>
            </div>
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Items</h2>
            <Select
              isMulti
              options={itemNameSelectOptions}
              onChange={handleItemNameFilterChange as any}
              placeholder="Select item names..."
              className="react-select-container"
              classNamePrefix="react-select"
              styles={{
                control: (base) => ({
                  ...base,
                  borderColor: 'var(--orange)',
                  '&:hover': {
                    borderColor: 'var(--pink1)',
                  },
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isSelected ? 'var(--orange)' : 'white',
                  color: state.isSelected ? 'white' : 'black',
                  '&:hover': {
                    backgroundColor: 'var(--pink1)',
                  },
                }),
              }}
            />
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Tags</h2>
            <Select
              isMulti
              options={itemTagSelectOptions}
              onChange={handleTagFilterChange as any}
              placeholder="Select tags..."
              className="react-select-container"
              classNamePrefix="react-select"
              styles={{
                control: (base) => ({
                  ...base,
                  borderColor: 'var(--orange)',
                  '&:hover': {
                    borderColor: 'var(--pink1)',
                  },
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isSelected ? 'var(--orange)' : 'white',
                  color: state.isSelected ? 'white' : 'black',
                  '&:hover': {
                    backgroundColor: 'var(--pink1)',
                  },
                }),
              }}
            />
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Effects</h2>
            <Select
              isMulti
              options={itemEffectSelectOptions}
              onChange={handleEffectFilterChange as any}
              placeholder="Select effects..."
              className="react-select-container"
              classNamePrefix="react-select"
              styles={{
                control: (base) => ({
                  ...base,
                  borderColor: 'var(--orange)',
                  '&:hover': {
                    borderColor: 'var(--pink1)',
                  },
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isSelected ? 'var(--orange)' : 'white',
                  color: state.isSelected ? 'white' : 'black',
                  '&:hover': {
                    backgroundColor: 'var(--pink1)',
                  },
                }),
              }}
            />
          </div>
        </div>
      </aside>

      <div className="p-4 ml-8 flex items-center flex-col gap-y-4">
        {paginatedItems.map((item, index) => (
          <ItemPreView key={index} item={item} />
        ))}

        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-6">
            <button
              onClick={() => {
                setCurrentPage((prev) => Math.max(prev - 1, 1));
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              disabled={currentPage === 1}
              className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                shadow-sm hover:shadow-md"
            >
              Previous
            </button>
            <span className="text-gray-600 font-medium">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => {
                setCurrentPage((prev) => Math.min(prev + 1, totalPages));
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              disabled={currentPage === totalPages}
              className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                shadow-sm hover:shadow-md"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
