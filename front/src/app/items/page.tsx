"use client";
import SelectedItems from "../components/SelectedItems";
import { useStaticData } from "../components/StaticDataContext";
import { useRouter } from "next/navigation";

export default function ItemsPage() {
  const { items, tags, effects } = useStaticData();
  const router = useRouter();

  if (!items || items.length === 0) {
    router.push("/error/wrong");
  }
  if (!effects || effects.length === 0) {
    router.push("/error/wrong");
  }
  if (!tags || tags.length === 0) {
    router.push("/error/wrong");
  }

  return <SelectedItems items={items} tags={tags} effects={effects} />;
} 