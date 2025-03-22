import { useRouter } from "next/navigation";
import { APIError } from "../interfaces/APIResponse";
import { useEffect } from "react";

export function useErrorRedirect(error: APIError) {
  const router = useRouter();
  useEffect(() => {
    if (error) {
      if (error.status == 401) {
        router.push("/error/unauthorized");
      } else {
        router.push("/error/wrong");
      }
    }
  }, [error, router]);
}
