"use client";
import { useEffect, Suspense } from "react";
import SelectedItems from "../components/SelectedItems";
import { useStaticData } from "../components/StaticDataContext";
import { useRouter, useSearchParams } from "next/navigation";

function ItemsContent({
  items,
  tags,
  effects,
}: {
  items: any;
  tags: any;
  effects: any;
}) {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get("search");

  return (
    <SelectedItems
      items={items}
      tags={tags}
      effects={effects}
      initialSearch={searchQuery}
    />
  );
}

export default function ItemsPage() {
  const { items, tags, effects } = useStaticData();
  const router = useRouter();

  useEffect(() => {
    if (
      !items ||
      items.length === 0 ||
      !effects ||
      effects.length === 0 ||
      !tags ||
      tags.length === 0
    ) {
      router.push("/error/wrong");
    }
  }, [items, tags, effects, router]);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ItemsContent items={items} tags={tags} effects={effects} />
    </Suspense>
  );
}
