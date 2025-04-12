import ReviewHistory from "@/app/components/ReviewHistory";

export default async function OrderHistoryPage({
  params,
}: {
  params: Promise<{ user_name: string }>;
}) {
  // Replace %20 with a space.
  return <ReviewHistory />;
}
