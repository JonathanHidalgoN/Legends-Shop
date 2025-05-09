"use client";
import { useState, useEffect, useRef, RefObject } from "react";
import Link from "next/link";
import { Item } from "../interfaces/Item";
import Image from "next/image";
import { useRouter } from "next/navigation";

function getItemMatches(query: string, items: Item[]): Item[] {
  if (query.length > 0) {
    return items.filter((item: Item) =>
      item.name.toLowerCase().includes(query.toLowerCase()),
    );
  } else {
    return [];
  }
}

export default function SearchBar({ items }: { items: Item[] }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Item[]>([]);
  const containerRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Update suggestions based on the query and items
  useEffect(() => {
    setSuggestions(getItemMatches(query, items));
  }, [query, items]);

  // Hide suggestions when clicking outside
  // source: https://stackoverflow.com/questions/32553158/detect-click-outside-react-component
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setSuggestions([]);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  //No need to use the effect because the event occurs directly on the input
  //For events like click outside componenet the event happens anywhere in the doc
  function handleFocus() {
    if (query.length > 0) {
      const matches = items.filter((item: Item) =>
        item.name.toLowerCase().includes(query.toLowerCase()),
      );
      setSuggestions(matches);
    }
  }

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/items?search=${encodeURIComponent(query.trim())}`);
      setQuery("");
      setSuggestions([]);
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search items..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={handleFocus}
          className="p-2 border rounded w-full"
        />
      </form>
      {query.length > 0 && suggestions.length > 0 && (
        <ul className="absolute bg-white border mt-1 w-full max-h-60 overflow-y-auto z-10 shadow-lg">
          {suggestions.map((item: Item, idx: number) => (
            <li key={idx} className="flex items-center p-2 hover:bg-gray-100">
              <Image
                src={item.img}
                alt={item.name}
                width={32}
                height={32}
                className="mr-2"
              />
              <Link href={`/items/${item.name}`}>
                <div onClick={() => setSuggestions([])}>{item.name}</div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
