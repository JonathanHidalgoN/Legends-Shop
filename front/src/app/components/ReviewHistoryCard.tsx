"use client";
import React from "react";
import { Review } from "@/app/interfaces/Review";
import { useStaticData } from "./StaticDataContext";
import Image from "next/image";

export default function ReviewHistoryCard({ review }: { review: Review }) {
  const { items } = useStaticData();
  
  // Find the item associated with this review
  const item = items.find((i) => i.id === review.itemId);
  
  // Format date
  const formattedDate = new Date(review.createdAt).toLocaleDateString();
  
  // Render stars based on rating
  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= review.rating) {
        stars.push(
          <span key={i} className="text-yellow-400 text-xl">★</span>
        );
      } else {
        stars.push(
          <span key={i} className="text-gray-300 text-xl">☆</span>
        );
      }
    }
    return stars;
  };

  return (
    <div className="flex border-b border-gray-200 py-3 last:border-b-0">
      {/* Item Image Section */}
      <div className="w-16 h-16 flex-shrink-0 mr-3">
        {item?.img ? (
          <div className="relative w-full h-full">
            <Image
              src={item.img}
              alt={item?.name || "Item"}
              fill
              className="object-cover rounded"
            />
          </div>
        ) : (
          <div className="w-full h-full bg-gray-200 rounded flex items-center justify-center">
            <span className="text-gray-400 text-xs">No image</span>
          </div>
        )}
      </div>
      
      {/* Review Content Section */}
      <div className="flex-grow">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-[var(--orange)]">
            {item?.name || "Unknown Item"}
          </h3>
          <span className="text-xs text-gray-500">
            {formattedDate}
          </span>
        </div>
        
        <div className="flex items-center mt-1">
          {renderStars()}
          <span className="ml-2 text-sm font-medium">
            {review.rating}/5
          </span>
        </div>
        
        {review.comments && review.comments.length > 0 && (
          <div className="mt-1">
            <p className="text-sm text-gray-700 italic">
              "{review.comments[0].content}"
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 