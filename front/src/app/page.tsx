"use client";
import SelectedItems from "./components/SelectedItems";
import { useStaticData } from "./components/StaticDataContext";
import { useRouter } from "next/navigation";

export default function Home() {
  const { items, tags } = useStaticData();
  const router = useRouter();

  if (!items || items.length === 0) {
    router.push("/error/wrong")
  }

  return <SelectedItems items={items} tags={tags} />;
}
