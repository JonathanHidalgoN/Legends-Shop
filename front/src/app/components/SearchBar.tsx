"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { Item } from "../interfaces/Item";

export default function SearchBar({ items }: { items: Item[] }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Item[]>([]);

  // This effect will trigger every time items or the query changes rendering a new search 
  // bar with the matches
  useEffect(() => {
    if (query.length > 0) {
      const matches = items.filter((item: Item) =>
        item.name.toLowerCase().includes(query.toLowerCase())
      );
      setSuggestions(matches);
    } else {
      setSuggestions([]);
    }
  }, [query, items]);

  return (
    <div className="relative">
      <input
        type="text"
        placeholder="Search items..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="p-2 border rounded w-full"
      />
      {query.length > 0 && suggestions.length > 0 && (
        <ul className="absolute bg-white border mt-1 w-full max-h-60 overflow-y-auto z-10 shadow-lg">
          {suggestions.map((item: Item, idx: number) => (
            <li key={idx} className="flex items-center p-2 hover:bg-gray-100">
              <img src={item.img} alt={item.name} className="w-8 h-8 mr-2" />
              <Link href={`/items/${item.name}`}>
                {/* Clean the search bar suggestions */}
                <div onClick={() => setQuery("")}>{item.name}</div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
