"use client";
import { useEffect } from "react";
import SelectedItems from "../components/SelectedItems";
import { useStaticData } from "../components/StaticDataContext";
import { useRouter, useSearchParams } from "next/navigation";

export default function ItemsPage() {
  const { items, tags, effects } = useStaticData();
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get("search");

  useEffect(() => {
    if (!items || items.length === 0 || !effects || effects.length === 0 || !tags || tags.length === 0) {
      router.push("/error/wrong");
    }
  }, [items, tags, effects, router]);

  return (
    <SelectedItems
      items={items}
      tags={tags}
      effects={effects}
      initialSearch={searchQuery}
    />
  );
}
