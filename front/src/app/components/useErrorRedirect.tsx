import { useRouter } from "next/navigation";
import { APIError } from "../interfaces/APIResponse";
import { useEffect } from "react";
import useSWR from "swr";
import { FromValues } from "../request";

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


export function useSWRWithErrorRedirect<T>(
  requestFunction: (from: FromValues) => Promise<T>,
  configFunction: () => any
) {
  const { data, mutate, error } = useSWR<T>(configFunction, requestFunction);
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
  return { data, mutate }
}
