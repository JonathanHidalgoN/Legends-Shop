import OrderHistory from "@/app/components/OrderHistory";

export default async function OrderHistoryPage({
  params,
}: {
  params: Promise<{ user_name: string }>;
}) {
  // Replace %20 with a space.
  return <OrderHistory />;
}
