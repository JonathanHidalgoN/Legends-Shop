import ReviewPage from "@/app/components/ReviewPage";

export default async function ReviewPageRoute({
  params,
  searchParams,
}: {
  params: Promise<{ order_id: string }>;
  searchParams: { isNew?: string };
}) {
  const idString: string = (await params).order_id;
  const isNew = searchParams.isNew === "true";
  
  return <ReviewPage orderId={parseInt(idString)} isNew={isNew} />;
} 
