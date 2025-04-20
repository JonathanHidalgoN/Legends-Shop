"use client";

import Image from "next/image";
import { Item } from "../interfaces/Item";
import DescriptionTextMapper from "./DescriptionTextMapper";
import AddToCarButton from "./AddToCarButton";
import { useStaticData } from "./StaticDataContext";
import { useEffect, useState } from "react";
import { FromValues, getReviewsByItemIdRequest } from "../request";
import { APIReviewResponse, APIError } from "../interfaces/APIResponse";
import { Review } from "../interfaces/Review";
import { mapAPIReviewResponseToReview } from "../mappers";
import { showErrorToast } from "../customToast";
import Link from "next/link";

function ItemRecommendations({ currentItemId }: { currentItemId: number }) {
  const { items } = useStaticData();
  const [recommendedItems, setRecommendedItems] = useState<Item[]>([]);

  useEffect(() => {
    const availableItems = items.filter((item) => item.id !== currentItemId);
    const shuffled = [...availableItems].sort(() => 0.5 - Math.random());
    setRecommendedItems(shuffled.slice(0, 3));
  }, [items, currentItemId]);

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-[var(--orange)] mb-6">
        You might also like
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recommendedItems.map((item) => (
          <Link
            href={`/items/${item.name}`}
            key={item.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
          >
            <div className="relative h-48">
              <Image
                src={item.img}
                alt={item.name}
                fill
                style={{ objectFit: "cover" }}
                quality={100}
              />
            </div>
            <div className="p-4">
              <h3 className="text-lg font-semibold text-[var(--orange)]">
                {item.name}
              </h3>
              <p className="text-[var(--yellow)] mt-1">{item.gold.base} g</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function ItemView({ itemName }: { itemName: string }) {
  const { items } = useStaticData();
  const item: Item | undefined = items.find((i) => i.name === itemName);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<APIError | null>(null);
  const [averageRating, setAverageRating] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const reviewsPerPage = 5;

  useEffect(() => {
    const fetchReviews = async () => {
      if (!item) return;

      try {
        setIsLoading(true);
        const apiReviews = await getReviewsByItemIdRequest(
          item.id,
          FromValues.CLIENT,
        );
        const mappedReviews = apiReviews.map(mapAPIReviewResponseToReview);
        setReviews(mappedReviews);

        // Calculate average rating
        if (mappedReviews.length > 0) {
          const totalRating = mappedReviews.reduce(
            (sum, review) => sum + review.rating,
            0,
          );
          setAverageRating(totalRating / mappedReviews.length);
        }
      } catch (err) {
        if (err instanceof APIError) {
          setError(err);
        } else {
          setError(new APIError("Failed to load reviews", 500));
        }
        showErrorToast("Failed to load reviews");
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviews();
  }, [item]);

  // Calculate pagination
  const totalPages = Math.ceil(reviews.length / reviewsPerPage);
  const startIndex = (currentPage - 1) * reviewsPerPage;
  const paginatedReviews = reviews.slice(
    startIndex,
    startIndex + reviewsPerPage,
  );

  if (!item) return <div>Item not found</div>;

  // Format date to a readable string
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="max-w-5xl mx-auto p-4 flex flex-col">
      <div className="flex flex-col md:flex-row">
        <div className="md:w-1/2">
          <div className="relative w-full h-96 rounded overflow-hidden shadow-lg">
            <Image
              src={item.img}
              alt={item.name}
              fill
              style={{ objectFit: "cover" }}
              quality={100}
            />
          </div>
        </div>

        <div className="md:w-1/2 md:ml-6 mt-4 md:mt-0">
          <h1 className="text-4xl font-bold text-[var(--orange)]">
            {item.name}
          </h1>
          <p className="mt-2 text-2xl text-[var(--yellow)]">
            {item.gold.base} g
          </p>

          <div className="mt-4 text-gray-700">
            <span className="font-bold">Description: </span>
            <DescriptionTextMapper description={item.description} />
          </div>

          {item.stats && item.stats.length > 0 && (
            <div className="mt-4">
              <span className="font-bold">Stats:</span>
              <ul className="list-disc list-inside">
                {item.stats.map((stat, index) => (
                  <li key={index}>
                    <span className="text-[var(--orange)]">
                      {stat.value}
                      {stat.kind === 0 ? "" : "%"}
                    </span>{" "}
                    {stat.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {item.effects && item.effects.length > 0 && (
            <div className="mt-4">
              <span className="font-bold">Effects:</span>
              <ul className="list-disc list-inside">
                {item.effects.map((effect, index) => (
                  <li key={index}>
                    <span className="text-[var(--pink1)]">{effect.value}</span>{" "}
                    {effect.name}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <AddToCarButton item={item} />
        </div>
      </div>

      <div className="mt-12">
        <h2 className="text-2xl font-bold text-[var(--orange)] mb-4">
          Reviews
        </h2>

        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
          </div>
        ) : reviews.length > 0 ? (
          <>
            <div className="flex items-center mb-6">
              <div className="flex items-center">
                <span className="text-3xl font-bold mr-2">
                  {averageRating.toFixed(1)}
                </span>
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg
                      key={star}
                      className={`w-6 h-6 ${
                        star <= Math.round(averageRating)
                          ? "text-yellow-400"
                          : "text-gray-300"
                      }`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
              </div>
              <span className="ml-4 text-gray-600">
                Based on {reviews.length}{" "}
                {reviews.length === 1 ? "review" : "reviews"}
              </span>
            </div>

            <div className="space-y-6">
              {paginatedReviews.map((review) => (
                <div
                  key={review.id}
                  className="bg-white rounded-lg shadow-md p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center">
                        <div className="flex">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <svg
                              key={star}
                              className={`w-5 h-5 ${
                                star <= review.rating
                                  ? "text-yellow-400"
                                  : "text-gray-300"
                              }`}
                              fill="currentColor"
                              viewBox="0 0 20 20"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                          ))}
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {formatDate(review.updatedAt || review.createdAt)}
                      </p>
                    </div>
                  </div>

                  {review.comments && review.comments.length > 0 ? (
                    <div className="mt-2">
                      <p className="text-gray-700">
                        {review.comments[0].content}
                      </p>
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No comment provided</p>
                  )}
                </div>
              ))}
            </div>
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
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No reviews yet for this item</p>
          </div>
        )}
      </div>

      <ItemRecommendations currentItemId={item.id} />
    </div>
  );
}
