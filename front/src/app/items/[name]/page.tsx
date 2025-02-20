export default async function Page({
  params,
}: {
  params: Promise<{ name: string }>
}) {
  const itemName = (await params).name
  return <div>My Post: {itemName}</div>
}
