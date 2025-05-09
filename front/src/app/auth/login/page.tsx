"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import LoginForm from "@/app/components/LoginForm";

function LogInContent() {
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/";

  return (
    <div className="bg-[var(--white)] min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Login</h1>
      <LoginForm redirectPath={redirect} />
    </div>
  );
}

export default function LogInPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LogInContent />
    </Suspense>
  );
}
