"use client";
import React, { useState, useMemo } from "react";
import ReviewHistoryCard from "@/app/components/ReviewHistoryCard";
import { Review } from "@/app/interfaces/Review";
import { APIReviewResponse } from "../interfaces/APIResponse";
import { mapAPIReviewResponseToReview } from "../mappers";
import { getUserReviewsRequest } from "@/app/request";
import useSWR from "swr";
import { useStaticData } from "./StaticDataContext";
import { useErrorRedirect } from "./useErrorRedirect";
import { useRouter } from "next/navigation";
import { showSuccessToast } from "@/app/customToast";

export default function ReviewHistory() {
  const { items } = useStaticData();
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState<number>(1);
  const reviewsPerPage = 5;
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch reviews using SWR with revalidation on focus
  const { data, error, mutate } = useSWR<APIReviewResponse[]>(
    ["reviews", "client"],
    getUserReviewsRequest,
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 0, // No automatic refresh
    },
  );

  // Handle errors with the error redirect hook
  useErrorRedirect(error);

  // Map API responses to Review objects - moved outside of conditional rendering
  const reviews: Review[] = useMemo(() => {
    if (!data) return [];
    return data.map(mapAPIReviewResponseToReview);
  }, [data]);

  // Group reviews by orderId
  const reviewsByOrder = useMemo(() => {
    const grouped: Record<number, Review[]> = {};

    reviews.forEach((review) => {
      if (!grouped[review.orderId]) {
        grouped[review.orderId] = [];
      }
      grouped[review.orderId].push(review);
    });

    return grouped;
  }, [reviews]);

  // Convert to array for pagination
  const orderIds = useMemo(
    () => Object.keys(reviewsByOrder).map(Number),
    [reviewsByOrder],
  );

  // Calculate pagination
  const totalPages = useMemo(
    () => Math.ceil(orderIds.length / reviewsPerPage),
    [orderIds, reviewsPerPage],
  );
  const startIndex = useMemo(
    () => (currentPage - 1) * reviewsPerPage,
    [currentPage, reviewsPerPage],
  );
  const paginatedOrderIds = useMemo(
    () => orderIds.slice(startIndex, startIndex + reviewsPerPage),
    [orderIds, startIndex, reviewsPerPage],
  );

  // Handle navigation to review page
  const handleReviewClick = (orderId: number) => {
    router.push(`/review/${orderId}?isNew=false`);
  };

  // Handle manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await mutate();
      showSuccessToast("Reviews refreshed successfully!");
    } catch (error) {
      console.error("Error refreshing reviews:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Show loading state
  if (!data || error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-6 p-4">
      <div className="flex justify-between items-center w-full max-w-2xl">
        <h1 className="text-2xl font-bold text-[var(--orange)] mb-4">
          Your Reviews
        </h1>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="px-4 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-opacity-90 
            transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
            shadow-sm hover:shadow-md flex items-center gap-2"
        >
          {isRefreshing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
              Refreshing...
            </>
          ) : (
            <>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                  clipRule="evenodd"
                />
              </svg>
              Refresh
            </>
          )}
        </button>
      </div>

      {paginatedOrderIds.length > 0 ? (
        <>
          {paginatedOrderIds.map((orderId) => (
            <div key={orderId} className="w-full max-w-2xl">
              <div
                className="border rounded-lg shadow-md overflow-hidden mb-4 cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => handleReviewClick(orderId)}
              >
                <div className="bg-[var(--orange)] text-white p-3 flex justify-between items-center">
                  <h2 className="font-bold">Order #{orderId}</h2>
                  <span className="text-sm">Click to view/edit reviews</span>
                </div>
                <div className="p-4">
                  {reviewsByOrder[orderId].map((review) => (
                    <ReviewHistoryCard key={review.id} review={review} />
                  ))}
                </div>
              </div>
            </div>
          ))}

          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4 mt-6">
              <button
                onClick={() => {
                  setCurrentPage((prev) => Math.max(prev - 1, 1));
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                disabled={currentPage === 1}
                className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                shadow-sm hover:shadow-md"
              >
                Previous
              </button>
              <span className="text-gray-600 font-medium">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => {
                  setCurrentPage((prev) => Math.min(prev + 1, totalPages));
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                disabled={currentPage === totalPages}
                className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                shadow-sm hover:shadow-md"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center text-gray-500 py-12 text-lg">
          You haven't written any reviews yet.
        </div>
      )}
    </div>
  );
}
