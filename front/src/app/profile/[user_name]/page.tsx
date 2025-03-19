import ProfileView from "@/app/components/ProfileView";

export default async function ProfilePage({
  params,
}: {
  params: Promise<{ user_name: string }>;
}) {
  // Replace %20 with a space.
  const urlUserName = (await params).user_name.replace(/%20/g, " ");
  return (
    <div>
      <ProfileView userName={urlUserName} />
    </div>
  );
}
