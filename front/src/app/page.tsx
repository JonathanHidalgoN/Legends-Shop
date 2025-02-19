import ItemPreView from "./components/ItemPreView";
import MainLateralPanel from "./components/MainLateralPanel";
import { Item } from "./interfaces/Item";
import { fetchItems, fetchTags } from "./itemsFetcher";

export default async function Home() {
  let items: Item[] = [];
  let tags: string[] = [];
  try {
    items = await fetchItems();
    tags = await fetchTags();
  } catch (error) {
    console.log(error);
    return <div>Error</div>;
  }

  if (!items || items.length === 0) {
    return <div>Error</div>;
  }

  console.log(tags)

  return (
    <div className="grid grid-cols-[15%_auto] h-full">
      <MainLateralPanel tags={tags} maxPrice={10000} />

      <div className="p-4 m-6 flex flex-wrap gap-x-10">
        {items.map((item, index) => (
          <ItemPreView key={index} item={item} />
        ))}
      </div>
    </div>
  );
}
