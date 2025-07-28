from fastapi import APIRouter, HTTPException
from app.database import db
from app.models import PropertyIn, Review
from bson import ObjectId

router = APIRouter()

@router.post("/properties/")
async def add_property(prop: PropertyIn):
    result = await db.properties.insert_one(prop.dict())
    return {"id": str(result.inserted_id)}

@router.get("/properties/")
async def list_properties():
    props = await db.properties.find().to_list(100)
    for prop in props:
        prop["id"] = str(prop["_id"])
        del prop["_id"]
    return props

@router.get("/properties/{property_id}")
async def get_property(property_id: str):
    try:
        prop = await db.properties.find_one({"_id": ObjectId(property_id)})
        if prop is None:
            raise HTTPException(status_code=404, detail="Property not found")
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        return prop
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid property ID")

@router.post("/properties/{property_id}/reviews")
async def add_review(property_id: str, review: Review):
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

@router.put("/properties/{property_id}")
async def update_property(property_id: str, prop_update: PropertyIn):
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

@router.get("/properties/{property_id}/availability")
async def check_property_availability(property_id: str, from_date: str, to_date: str):
    """Check if property is available for given dates based on occupancy"""
    try:
        from datetime import datetime
        from app.database import db
        
        # Get property details
        prop = await db.properties.find_one({"_id": ObjectId(property_id)})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        total_rooms = prop.get("rooms", 1)
        
        # Parse dates
        start_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        
        # Count existing bookings for the date range
        existing_bookings = await db.bookings.count_documents({
            "property_id": property_id,
            "$or": [
                {
                    "from_date": {"$lt": end_date},
                    "to_date": {"$gt": start_date}
                }
            ]
        })
        
        available_rooms = total_rooms - existing_bookings
        is_available = available_rooms > 0
        
        return {
            "property_id": property_id,
            "total_rooms": total_rooms,
            "booked_rooms": existing_bookings,
            "available_rooms": available_rooms,
            "is_available": is_available,
            "from_date": from_date,
            "to_date": to_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error checking availability: {str(e)}")