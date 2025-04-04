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

export default function ReviewHistory() {
  const { items } = useStaticData();
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState<number>(1);
  const reviewsPerPage = 5;

  // Fetch reviews using SWR
  const { data, error } = useSWR<APIReviewResponse[]>(
    ["reviews", "client"],
    getUserReviewsRequest
  );

  // Handle errors with the error redirect hook
  useErrorRedirect(error);

  // Show loading state
  if (!data || error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
      </div>
    );
  }

  // Map API responses to Review objects
  const reviews: Review[] = data.map(mapAPIReviewResponseToReview);

  // Group reviews by orderId
  const reviewsByOrder = useMemo(() => {
    const grouped: Record<number, Review[]> = {};
    
    reviews.forEach(review => {
      if (!grouped[review.orderId]) {
        grouped[review.orderId] = [];
      }
      grouped[review.orderId].push(review);
    });
    
    return grouped;
  }, [reviews]);

  // Convert to array for pagination
  const orderIds = Object.keys(reviewsByOrder).map(Number);
  
  // Calculate pagination
  const totalPages = Math.ceil(orderIds.length / reviewsPerPage);
  const startIndex = (currentPage - 1) * reviewsPerPage;
  const paginatedOrderIds = orderIds.slice(startIndex, startIndex + reviewsPerPage);

  // Handle navigation to review page
  const handleReviewClick = (orderId: number) => {
    router.push(`/review/${orderId}?isNew=false`);
  };

  return (
    <div className="flex flex-col items-center gap-6 p-4">
      <h1 className="text-2xl font-bold text-[var(--orange)] mb-4">Your Reviews</h1>
      
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
