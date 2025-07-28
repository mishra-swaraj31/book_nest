from fastapi import APIRouter, HTTPException
from app.database import db
from app.models import BookingIn
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

router = APIRouter()

class BookingUpdate(BaseModel):
    from_date: datetime
    to_date: datetime
    guests: int = 1

@router.post("/bookings/Create")
async def bookings_create(booking: BookingIn):
    print(f"Received booking request: {booking}")
    booking_data = booking.dict()
    # Calculate total cost if not provided
    if booking_data.get("total_cost", 0) == 0:
        try:
            property_doc = await db.properties.find_one({"_id": ObjectId(booking.property_id)})
            if property_doc:
                from_date = booking.from_date
                to_date = booking.to_date
                days = (to_date - from_date).days
                price_per_night = property_doc.get("price_per_night", 0)
                booking_data["total_cost"] = days * price_per_night
                print(f"Calculated total cost: {booking_data['total_cost']} for {days} days at ${price_per_night}/night")
            else:
                print("Property not found for cost calculation")
        except Exception as e:
            print(f"Error calculating total cost: {e}")
    print(f"Booking data to insert: {booking_data}")
    result = await db.bookings.insert_one(booking_data)
    print(f"Booking created with ID: {result.inserted_id}")
    return {"id": str(result.inserted_id)}

@router.get("/bookings/ReadAll")
async def bookings_read_all():
    bookings = await db.bookings.find().to_list(100)
    for booking in bookings:
        booking["id"] = str(booking["_id"])
        del booking["_id"]
    return bookings

@router.delete("/bookings/Delete/{booking_id}")
async def bookings_delete(booking_id: str):
    try:
        result = await db.bookings.delete_one({"_id": ObjectId(booking_id)})
        if result.deleted_count == 0:
            return {"error": "Booking not found"}
        return {"message": "Booking deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete booking: {str(e)}"}

@router.put("/bookings/Update/{booking_id}")
async def bookings_update(booking_id: str, update: BookingUpdate):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    property_doc = await db.properties.find_one({"_id": ObjectId(booking["property_id"])})
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")

    days = (update.to_date - update.from_date).days
    price_per_night = property_doc.get("price_per_night", 0)
    total_cost = days * price_per_night

    update_data = {
        "from_date": update.from_date,
        "to_date": update.to_date,
        "guests": update.guests,
        "total_cost": total_cost
    }
    await db.bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": update_data})
    return {"message": "Booking updated", "total_cost": total_cost}