
export default async function OrderHistoryPage({ params }: { params: Promise<{ user_name: string }> }) {
  //Replace the %20 for a space
  const userName: string = (await params).user_name.replace(/%20/g, " ");
  return (<div>
    {userName}
  </div>)
}
