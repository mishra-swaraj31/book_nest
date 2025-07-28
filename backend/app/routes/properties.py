from fastapi import APIRouter, HTTPException
from app.database import db
from app.models import PropertyIn, Review
from bson import ObjectId
from fastapi import Query
from typing import Optional
import pymongo

router = APIRouter()

@router.post("/property/Create")
async def property_create(prop: PropertyIn):
    result = await db.properties.insert_one(prop.dict())
    return {"id": str(result.inserted_id)}

@router.get("/property/ReadAll")
async def property_read_all():
    props = await db.properties.find().to_list(100)
    for prop in props:
        prop["id"] = str(prop["_id"])
        del prop["_id"]
    return props

@router.get("/property/Read/{property_id}")
async def property_read(property_id: str):
    try:
        prop = await db.properties.find_one({"_id": ObjectId(property_id)})
        if prop is None:
            raise HTTPException(status_code=404, detail="Property not found")
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        return prop
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid property ID")

@router.post("/property/CreateReview/{property_id}")
async def property_create_review(property_id: str, review: Review):
    try:
        result = await db.properties.update_one(
            {"_id": ObjectId(property_id)},
            {"$push": {"reviews": review.dict()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Property not found")
        return {"message": "Review added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid property ID")

@router.put("/property/Update/{property_id}")
async def property_update(property_id: str, prop_update: PropertyIn):
    try:
        result = await db.properties.update_one(
            {"_id": ObjectId(property_id)},
            {"$set": prop_update.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Property not found")
        return {"message": "Property updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid property ID")

@router.get("/property/ReadAvailability/{property_id}")
async def property_read_availability(property_id: str, from_date: str, to_date: str):
    """
    Check property availability across date range by counting overlapping bookings per day
    """
    try:
        # Convert date strings to datetime
        start_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Invalid date range")

        # Fetch property
        prop = await db.properties.find_one({"_id": ObjectId(property_id)})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        total_rooms = prop.get("rooms", 1)

        # Fetch all bookings that overlap any day in this range
        overlapping_bookings = await db.bookings.find({
            "property_id": property_id,
            "from_date": {"$lt": end_date},
            "to_date": {"$gt": start_date}
        }).to_list(length=1000)

        # Initialize date-wise booking counter
        date_bookings = {}

        current_date = start_date
        while current_date < end_date:
            date_bookings[current_date.date()] = 0
            current_date += timedelta(days=1)

        # Count how many rooms are booked on each date
        for booking in overlapping_bookings:
            b_from = booking["from_date"].date()
            b_to = booking["to_date"].date()
            guests = booking.get("guests", 1)

            temp_date = max(start_date.date(), b_from)
            while temp_date < min(end_date.date(), b_to):
                if temp_date in date_bookings:
                    date_bookings[temp_date] += guests
                temp_date += timedelta(days=1)

        # Check availability for each date
        unavailable_dates = [date for date, booked in date_bookings.items() if booked >= total_rooms]

        return {
            "property_id": property_id,
            "total_rooms": total_rooms,
            "date_bookings": date_bookings,
            "unavailable_dates": unavailable_dates,
            "is_available": len(unavailable_dates) == 0,
            "from_date": from_date,
            "to_date": to_date
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error checking availability: {str(e)}")

@router.get("/property/ReadAll")
async def property_read_all(
    location: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    min_rooms: Optional[int] = Query(None, ge=1, description="Minimum number of rooms"),
    available: Optional[bool] = None,
    sort_by: Optional[str] = Query(None, description="Field to sort by, e.g., 'price_per_night'"),
    sort_order: str = Query("asc", description="'asc' or 'desc'"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Number of records to return")
):
    """
    Reads properties with filtering, sorting, and pagination.
    """
    query = {}

    # --- 1. Build the filter query dynamically ---
    if location:
        # Use regex for a case-insensitive partial match
        query["location"] = {"$regex": location, "$options": "i"}
    
    price_query = {}
    if min_price is not None:
        price_query["$gte"] = min_price
    if max_price is not None:
        price_query["$lte"] = max_price
    if price_query:
        query["price_per_night"] = price_query

    if min_rooms is not None:
        query["rooms"] = {"$gte": min_rooms}
        
    if available is not None:
        query["available"] = available

    # --- 2. Get total count for pagination ---
    total_count = await db.properties.count_documents(query)

    # --- 3. Apply sorting and pagination to the cursor ---
    cursor = db.properties.find(query)
    
    if sort_by:
        direction = pymongo.ASCENDING if sort_order.lower() == "asc" else pymongo.DESCENDING
        cursor = cursor.sort(sort_by, direction)
        
    cursor = cursor.skip(skip).limit(limit)

    # --- 4. Fetch and format the results ---
    properties = await cursor.to_list(length=limit)
    for prop in properties:
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        
    return {"total": total_count, "properties": properties}