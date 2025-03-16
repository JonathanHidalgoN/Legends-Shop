import ItemView from "@/app/components/ItemView";

export default async function ItemPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  //Replace the %20 for a space
  const itemName: string = (await params).name.replace(/%20/g, " ");
  return <ItemView itemName={itemName} />;
}
