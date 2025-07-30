# routes/owners.py
from fastapi import APIRouter, HTTPException
from app.models import HotelOwner
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/owner/create")
async def create_owner(owner: HotelOwner):
    existing = await db.hotel_owners.find_one({"owner_id": owner.owner_id})
    if existing:
        raise HTTPException(status_code=400, detail="Owner already exists")
    result = await db.hotel_owners.insert_one(owner.dict())
    return {"id": str(result.inserted_id)}

@router.post("/owner/add-property/{owner_id}/{property_id}")
async def add_property_to_owner(owner_id: str, property_id: str):
    result = await db.hotel_owners.update_one(
        {"owner_id": owner_id},
        {"$addToSet": {"property_ids": property_id}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Owner not found or already has property")
    return {"message": "Property added to owner"}

@router.get("/owner/properties/{owner_id}")
async def get_owner_properties(owner_id: str):
    owner = await db.hotel_owners.find_one({"owner_id": owner_id})
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    props = await db.properties.find({"_id": {"$in": [ObjectId(pid) for pid in owner["property_ids"]]}}).to_list(100)
    for p in props:
        p["id"] = str(p["_id"])
        del p["_id"]
    return props

@router.get("/owner/all")
async def get_all_owners():
    owners = await db.hotel_owners.find().to_list(100)
    for o in owners:
        o["_id"] = str(o["_id"])
    return owners
