import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import (
    InvalidRatingException,
    InvalidUserReview,
    ReviewProcessorException,
)
from app.routes.auth import getUserIdFromName
from staticData import STATIC_REVIEW1, STATIC_REVIEW2

STATIC_REVIEWS = [STATIC_REVIEW1, STATIC_REVIEW2]

client = TestClient(app)


async def fake_getUserIdFromName() -> int:
    return 1


app.dependency_overrides[getUserIdFromName] = fake_getUserIdFromName


def reviewToDict(review):
    reviewDict = review.model_dump()
    reviewDict["createdAt"] = reviewDict["createdAt"].isoformat()
    reviewDict["updatedAt"] = reviewDict["updatedAt"].isoformat()

    if review.comments:
        for i, comment in enumerate(review.comments):
            commentDict = comment.model_dump()
            commentDict["createdAt"] = commentDict["createdAt"].isoformat()
            commentDict["updatedAt"] = commentDict["updatedAt"].isoformat()
            reviewDict["comments"][i] = commentDict
    return reviewDict


@pytest.mark.asyncio
async def test_add_review_success():
    """Test successful addition of a review."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.addReviewAndComments",
        new=AsyncMock(return_value=None),
    ):
        response = client.post("/review/add", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_review_invalid_user():
    """Test error handling when adding a review with invalid user."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.addReviewAndComments",
        new=AsyncMock(
            side_effect=InvalidUserReview("User is different to the order user")
        ),
    ):
        response = client.post("/review/add", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_review_error():
    """Test error handling when adding a review fails."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.addReviewAndComments",
        new=AsyncMock(side_effect=ReviewProcessorException("Internal server error")),
    ):
        response = client.post("/review/add", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_update_review_success():
    """Test successful update of a review."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.updateReviewAndComments",
        new=AsyncMock(return_value=None),
    ):
        response = client.put("/review/update", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_review_invalid_rating():
    """Test error handling when updating a review with invalid rating."""
    invalidReview = reviewToDict(STATIC_REVIEW1)
    invalidReview["rating"] = 0

    with pytest.raises(InvalidRatingException):
        client.put("/review/update", json=invalidReview)


@pytest.mark.asyncio
async def test_add_review_invalid_rating():
    """Test error handling when adding a review with invalid rating."""
    invalidReview = reviewToDict(STATIC_REVIEW1)
    invalidReview["rating"] = 6

    with pytest.raises(InvalidRatingException):
        client.post("/review/add", json=invalidReview)


@pytest.mark.asyncio
async def test_update_review_invalid_user():
    """Test error handling when updating a review with invalid user."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.updateReviewAndComments",
        new=AsyncMock(
            side_effect=InvalidUserReview("User is different to the order user")
        ),
    ):
        response = client.put("/review/update", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_review_error():
    """Test error handling when updating a review fails."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.updateReviewAndComments",
        new=AsyncMock(side_effect=ReviewProcessorException("Error updating review")),
    ):
        response = client.put("/review/update", json=reviewToDict(STATIC_REVIEW1))
        assert response.status_code == 500
        assert "Error updating review" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_reviews_by_user_success():
    """Test successful retrieval of user's reviews."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.getReviewsByUserId",
        new=AsyncMock(return_value=STATIC_REVIEWS),
    ):
        response = client.get("/review/user")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == STATIC_REVIEW1.id
        assert response.json()[1]["id"] == STATIC_REVIEW2.id


@pytest.mark.asyncio
async def test_get_reviews_by_user_error():
    """Test error handling when retrieving user's reviews fails."""
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.getReviewsByUserId",
        new=AsyncMock(side_effect=ReviewProcessorException("Error retrieving reviews")),
    ):
        response = client.get("/review/user")
        assert response.status_code == 500
        assert "Error retrieving reviews" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_reviews_by_item_success():
    """Test successful retrieval of item's reviews."""
    itemId = 1
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.getReviewsAndCommentsByItemId",
        new=AsyncMock(return_value=STATIC_REVIEWS),
    ):
        response = client.get(f"/review/item/{itemId}")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == STATIC_REVIEW1.id
        assert response.json()[1]["id"] == STATIC_REVIEW2.id


@pytest.mark.asyncio
async def test_get_reviews_by_item_error():
    """Test error handling when retrieving item's reviews fails."""
    itemId = 1
    with patch(
        "app.reviews.ReviewProcessor.ReviewProcessor.getReviewsAndCommentsByItemId",
        new=AsyncMock(
            side_effect=ReviewProcessorException("Error retrieving item reviews")
        ),
    ):
        response = client.get(f"/review/item/{itemId}")
        assert response.status_code == 500
