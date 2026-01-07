"""Review routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.dependencies.auth import (
    get_current_user,
    get_customer,
    get_restaurant_manager,
    get_restaurant_staff,
)
from src.api.dependencies.database import get_repository
from db.repositories.image import ReviewRepository
from src.enums.review_status import ReviewStatus
from models.image import ReviewAnalytics, ReviewCreate, ReviewPublic, ReviewSummary
from src.models.user import UserWithContext
from src.utils.auth import validate_customer_data_access, validate_restaurant_access

review_router = APIRouter()


@review_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a review",
    description="Create a new review for a restaurant. Only customers can create reviews.",
)
async def create_review(
    review_data: ReviewCreate,
    # user: UserWithContext = Depends(get_customer),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> ReviewPublic:
    """Create a new review."""
    created_review = await review_repo.create_review(review_data)
    return ReviewPublic(**created_review.model_dump())


@review_router.get(
    "/restaurant/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    summary="Get restaurant reviews",
    description="Get all reviews for a specific restaurant with optional filtering.",
)
async def get_restaurant_reviews(
    restaurant_id: UUID = Path(..., description="Restaurant identifier"),
    status: Optional[ReviewStatus] = Query(None, description="Filter by review status"),
    min_rating: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
    # user: UserWithContext = Depends(get_restaurant_manager),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> List[ReviewPublic]:
    """Get reviews for a specific restaurant."""
    return await review_repo.get_reviews(
        restaurant_id=restaurant_id,
        status=status,
        min_rating=min_rating,
        limit=limit,
        offset=offset,
    )


@review_router.get(
    "/customer/{customer_id}/restaurant/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    summary="Get customer reviews by restaurant",
    description="Retrieve all reviews for a specific customer at a restaurant.",
)
async def get_customer_reviews_by_restaurant(
    customer_id: UUID = Path(..., description="Customer identifier"),
    restaurant_id: UUID = Path(..., description="Restaurant identifier"),
    user: UserWithContext = Depends(get_restaurant_staff),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> List[ReviewPublic]:
    """Get all reviews for a customer at a specific restaurant."""
    validate_restaurant_access(user, restaurant_id, "view customer reviews")

    return await review_repo.get_reviews(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
    )


@review_router.get(
    "/customer/{customer_id}",
    status_code=status.HTTP_200_OK,
    summary="Get customer reviews",
    description="Get all reviews created by a specific customer.",
)
async def get_customer_reviews(
    customer_id: UUID = Path(..., description="Customer identifier"),
    limit: int = Query(50, ge=1, le=100, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
    user: UserWithContext = Depends(get_customer),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> List[ReviewPublic]:
    """Get reviews created by a specific customer."""
    validate_customer_data_access(user, customer_id, "view reviews")

    return await review_repo.get_reviews(
        customer_id=customer_id, limit=limit, offset=offset
    )


@review_router.get(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Get review by ID",
    description="Get a specific review by its ID.",
)
async def get_review(
    review_id: UUID = Path(..., description="Review identifier"),
    user: UserWithContext = Depends(get_current_user),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> ReviewPublic:
    """Get a specific review by ID."""
    review = await review_repo.get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@review_router.get(
    "/analytics/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    summary="Get review analytics",
    description="Get comprehensive review analytics for a restaurant. Requires restaurant staff access.",
)
async def get_review_analytics(
    restaurant_id: UUID = Path(..., description="Restaurant identifier"),
    user: UserWithContext = Depends(get_restaurant_manager),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> ReviewAnalytics:
    """Get review analytics for a restaurant."""
    validate_restaurant_access(user, restaurant_id, "view review analytics")

    return await review_repo.get_restaurant_review_analytics(restaurant_id)


@review_router.get(
    "/restaurant/{restaurant_id}/pending-responses",
    status_code=status.HTTP_200_OK,
    summary="Get reviews needing response",
    description="Get reviews that don't have restaurant responses yet. Requires restaurant staff access.",
)
async def get_reviews_needing_response(
    restaurant_id: UUID = Path(..., description="Restaurant identifier"),
    limit: int = Query(20, ge=1, le=50, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
    user: UserWithContext = Depends(get_restaurant_manager),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> List[ReviewSummary]:
    """Get reviews that need restaurant responses."""
    validate_restaurant_access(user, restaurant_id, "view pending reviews")

    return await review_repo.get_reviews_needing_response(
        restaurant_id=restaurant_id, limit=limit, offset=offset
    )


@review_router.post(
    "/{review_id}/respond",
    status_code=status.HTTP_200_OK,
    summary="Respond to review",
    description="Add a restaurant response to a review. Requires restaurant staff access.",
)
async def respond_to_review(
    review_id: UUID = Path(..., description="Review identifier"),
    response_text: str = Query(
        ..., min_length=1, max_length=1000, description="Restaurant response text"
    ),
    user: UserWithContext = Depends(get_restaurant_manager),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> ReviewPublic:
    """Add a restaurant response to a review."""
    review = await review_repo.get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    validate_restaurant_access(user, review.restaurant_id, "respond to reviews")

    if review.response_from_restaurant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already has a restaurant response",
        )

    updated_review = await review_repo.respond_to_review(review_id, response_text)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add response to review",
        )

    return updated_review


@review_router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review",
    description="Soft delete a review. Only customers can delete their own reviews or admins can delete any review.",
)
async def delete_review(
    review_id: UUID = Path(..., description="Review identifier"),
    user: UserWithContext = Depends(get_customer),
    review_repo: ReviewRepository = Depends(get_repository(ReviewRepository)),
) -> None:
    """Delete a review."""
    review = await review_repo.get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    validate_customer_data_access(user, review.customer_id, "delete review")

    success = await review_repo.delete_review(review_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete review"
        )
