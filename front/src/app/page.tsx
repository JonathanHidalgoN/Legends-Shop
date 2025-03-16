"use client";
import SelectedItems from "./components/SelectedItems";
import { useStaticData } from "./components/StaticDataContext";

export default function Home() {
  const { items, tags } = useStaticData();

  if (!items || items.length === 0) {
    return <div>Error</div>;
  }

  return <SelectedItems items={items} tags={tags} />;
}
