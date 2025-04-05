export interface Comment {
  id: number;
  reviewId: number;
  userId: number;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Review {
  id: number;
  orderId: number;
  itemId: number;
  rating: number;
  createdAt: Date;
  updatedAt: Date;
  comments: Comment[];
}
