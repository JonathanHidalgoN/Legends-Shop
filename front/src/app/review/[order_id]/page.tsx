import ReviewPage from "@/app/components/ReviewPage";

export default async function ReviewPageRoute({
  params,
  searchParams,
}: {
  params: Promise<{ order_id: string }>;
  searchParams: Promise<{ isNew?: string }>;
}) {
  const idString: string = (await params).order_id;
  const isNew = (await searchParams).isNew === "true";

  return <ReviewPage orderId={parseInt(idString)} isNew={isNew} />;
}
