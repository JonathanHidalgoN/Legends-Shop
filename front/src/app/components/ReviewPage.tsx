"use client";
import { Order } from "@/app/interfaces/Order";
import {
  APIOrderResponse,
  APIReviewResponse,
} from "@/app/interfaces/APIResponse";
import {
  FromValues,
  getOrderHistoryWithCredentialsRequest,
  getUserReviewsRequest,
} from "@/app/request";
import {
  mapAPIOrderResponseToOrder,
  mapAPIReviewResponseToReview,
} from "@/app/mappers";
import useSWR from "swr";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { addReviewRequest, updateReviewRequest } from "@/app/request";
import { Review } from "@/app/interfaces/Review";
import ReviewCard from "./ReviewCard";
import { useStaticData } from "./StaticDataContext";
import { useAuthContext } from "./AuthContext";
import { showSuccessToast } from "@/app/customToast";

export default function ReviewPage({
  orderId,
  isNew = true,
}: {
  orderId: number;
  isNew?: boolean;
}) {
  const { data: orderData, error: orderError } = useSWR<APIOrderResponse[]>(
    ["orders-client", FromValues.CLIENT],
    getOrderHistoryWithCredentialsRequest,
  );

  // Use SWR for fetching reviews when not a new review
  const { data: reviewData, mutate: mutateReviews } = useSWR<
    APIReviewResponse[]
  >(isNew ? null : ["reviews", "client"], getUserReviewsRequest);

  const { items } = useStaticData();
  const { userName } = useAuthContext();
  const router = useRouter();

  // Initialize reviews state
  const [reviews, setReviews] = useState<{
    [key: string]: { rating: number; comment: string };
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [existingReviewIds, setExistingReviewIds] = useState<{
    [key: string]: number;
  }>({});

  // Load existing reviews if not a new review
  useEffect(() => {
    if (!isNew && reviewData) {
      console.log("Loading existing reviews for order:", orderId);
      const existingReviews: {
        [key: string]: { rating: number; comment: string };
      } = {};
      const reviewIds: { [key: string]: number } = {};

      // Map API responses to Review objects
      const mappedReviews = reviewData.map(mapAPIReviewResponseToReview);
      console.log("Mapped reviews:", mappedReviews);

      // Filter reviews for this order
      const orderReviews = mappedReviews.filter(
        (review) => review.orderId === orderId,
      );
      console.log("Order reviews:", orderReviews);

      // Map reviews to the state format
      orderReviews.forEach((review) => {
        const itemName = items.find((item) => item.id === review.itemId)?.name;
        if (itemName) {
          existingReviews[itemName] = {
            rating: review.rating,
            comment:
              review.comments.length > 0 ? review.comments[0].content : "",
          };
          reviewIds[itemName] = review.id;
        }
      });

      console.log("Setting reviews state:", existingReviews);
      setReviews(existingReviews);
      setExistingReviewIds(reviewIds);
      setIsLoading(false);
    } else if (isNew) {
      setIsLoading(false);
    }
  }, [isNew, reviewData, orderId, items]);

  if (!orderData || orderError) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
      </div>
    );
  }

  const order = orderData
    .map((apiOrder: APIOrderResponse) => mapAPIOrderResponseToOrder(apiOrder))
    .find((order: Order) => order.id === orderId);

  if (!order) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Order not found</h1>
      </div>
    );
  }

  // Group items by name and count their occurrences
  const itemCounts = order.itemNames.reduce(
    (acc, name) => {
      acc[name] = (acc[name] || 0) + 1;
      return acc;
    },
    {} as { [key: string]: number },
  );

  // Get unique item names
  const uniqueItemNames = Object.keys(itemCounts);

  // Map item names to their actual IDs
  const itemNameToId = uniqueItemNames.reduce(
    (acc, name) => {
      const item = items.find((i) => i.name === name);
      if (item) {
        acc[name] = item.id;
      }
      return acc;
    },
    {} as { [key: string]: number },
  );

  const handleReviewChange = (
    itemName: string,
    rating: number,
    comment: string,
  ) => {
    setReviews((prev) => ({
      ...prev,
      [itemName]: { rating, comment },
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const reviewPromises = Object.entries(reviews).map(
        ([itemName, review]) => {
          const itemId = itemNameToId[itemName];
          if (!itemId) {
            console.error(`Item ID not found for ${itemName}`);
            return Promise.resolve();
          }

          const reviewData: Review = {
            id: isNew ? 0 : existingReviewIds[itemName] || 0, // Use existing ID if updating
            orderId: order.id,
            itemId: itemId,
            rating: review.rating,
            createdAt: new Date(),
            updatedAt: new Date(),
            comments: review.comment
              ? [
                  {
                    id: 0, // Will be set by backend
                    reviewId: isNew ? 0 : existingReviewIds[itemName] || 0, // Use existing review ID if updating
                    userId: 0, // Will be set by backend
                    content: review.comment,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                  },
                ]
              : [],
          };

          // Use the appropriate request function based on whether it's a new review or an update
          if (isNew) {
            return addReviewRequest(reviewData, FromValues.CLIENT);
          } else {
            return updateReviewRequest(reviewData, FromValues.CLIENT);
          }
        },
      );

      await Promise.all(reviewPromises);

      // Revalidate the reviews cache to ensure we have the latest data
      if (!isNew && mutateReviews) {
        await mutateReviews();
      }

      showSuccessToast(
        isNew
          ? "Reviews submitted successfully!"
          : "Reviews updated successfully!",
      );
      router.push(`/order/order_history/${userName}`);
    } catch (error) {
      console.error("Error submitting reviews:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--white)] text-[var(--black)]">
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ff8c00' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 animate-fade-in">
            <h1 className="text-3xl md:text-4xl font-bold text-[var(--orange)] mb-4 animate-slide-up">
              {isNew ? "Review Your Order" : "Edit Your Reviews"}
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-gray-700 animate-slide-up-delayed">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium text-[var(--orange)]">Order Date</p>
                <p>{order.orderDate.toLocaleDateString()}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium text-[var(--orange)]">
                  Delivery Date
                </p>
                <p>{order.deliveryDate.toLocaleDateString()}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium text-[var(--orange)]">Total</p>
                <p>{order.total} gold</p>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center min-h-[40vh]">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
            </div>
          ) : (
            <div className="space-y-6 animate-fade-in">
              {uniqueItemNames.map((itemName, index) => (
                <ReviewCard
                  key={index}
                  itemName={itemName}
                  itemId={itemNameToId[itemName] || 0}
                  quantity={itemCounts[itemName]}
                  onReviewChange={(_, rating, comment) =>
                    handleReviewChange(itemName, rating, comment)
                  }
                  initialRating={reviews[itemName]?.rating || 0}
                  initialComment={reviews[itemName]?.comment || ""}
                />
              ))}

              <div className="flex justify-end mt-8">
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting || Object.keys(reviews).length === 0}
                  className={`px-8 py-3 rounded-lg text-lg font-semibold transition-all duration-300 transform hover:scale-105 ${
                    isSubmitting || Object.keys(reviews).length === 0
                      ? "bg-gray-400 text-white cursor-not-allowed"
                      : "bg-[var(--orange)] text-white hover:bg-opacity-90"
                  }`}
                >
                  {isSubmitting
                    ? "Submitting..."
                    : isNew
                      ? "Submit Reviews"
                      : "Update Reviews"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
