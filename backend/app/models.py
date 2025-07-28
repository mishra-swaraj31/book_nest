from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Review model for property reviews
class Review(BaseModel):
    user_id: str
    user_name: str
    rating: int  # 1-5 stars
    comment: str
    created_at: datetime = datetime.now()

# Input model for adding a property (NO id)
class PropertyIn(BaseModel):
    name: str
    location: str
    price_per_night: float
    available: bool = True
    rooms: int = 1  # Total number of rooms available
    images: List[str] = []  # List of image URLs
    latitude: Optional[float] = None  # Map location latitude
    longitude: Optional[float] = None  # Map location longitude
    reviews: List[Review] = []  # Array of reviews

# Model for returning a property (includes id)
class Property(PropertyIn):
    id: str

class BookingIn(BaseModel):
    property_id: str
    from_date: datetime
    to_date: datetime
    user_id: str = "default-user"
    guests: int = 1
    total_cost: float = 0.0  # Total cost for the entire stay

# Model for returning a booking (includes id)
class Booking(BookingIn):
    id: str