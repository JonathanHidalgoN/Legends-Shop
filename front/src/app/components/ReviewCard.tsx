import { useState } from "react";
import { useStaticData } from "./StaticDataContext";
import Image from "next/image";

interface ReviewCardProps {
  itemName: string;
  itemId: number;
  quantity: number;
  onReviewChange: (itemId: number, rating: number, comment: string) => void;
  initialRating?: number;
  initialComment?: string;
}

export default function ReviewCard({
  itemName,
  itemId,
  quantity,
  onReviewChange,
  initialRating = 0,
  initialComment = "",
}: ReviewCardProps) {
  const { items } = useStaticData();
  const [rating, setRating] = useState(initialRating);
  const [comment, setComment] = useState(initialComment);

  const item = items.find(i => i.name === itemName);

  const handleRatingChange = (newRating: number) => {
    setRating(newRating);
    onReviewChange(itemId, newRating, comment);
  };

  const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newComment = e.target.value;
    setComment(newComment);
    onReviewChange(itemId, rating, newComment);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex flex-col md:flex-row items-start space-y-4 md:space-y-0 md:space-x-6">
        {item && (
          <div className="relative w-32 h-32 flex-shrink-0 mx-auto md:mx-0">
            <Image
              src={item.img}
              alt={itemName}
              fill
              className="object-contain rounded-lg border-2 border-[var(--orange)] shadow-md"
            />
          </div>
        )}
        <div className="flex-grow w-full">
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-[var(--orange)]">{itemName}</h2>
            <span className="inline-block bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium mt-2 md:mt-0">
              Quantity: {quantity}
            </span>
          </div>
          
          {item && (
            <div className="text-gray-700 mb-4">
              <span className="font-medium">Cost: </span>
              <span className="text-[var(--orange)] font-semibold">{item.gold.total} gold</span>
            </div>
          )}
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Rating</label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => handleRatingChange(star)}
                  className={`text-2xl transition-transform duration-200 hover:scale-110 ${
                    rating >= star ? 'text-[var(--orange)]' : 'text-gray-300'
                  }`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Comment</label>
            <textarea
              value={comment}
              onChange={handleCommentChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent transition-all duration-300"
              rows={3}
              placeholder="Share your experience with this item..."
            />
          </div>
        </div>
      </div>
    </div>
  );
} 