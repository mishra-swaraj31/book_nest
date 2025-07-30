from datetime import datetime, timedelta
import random
import requests

# Constants
property_url = "http://localhost:8000/property/Create"
owner_url = "http://localhost:8000/owner/create"
add_property_url = "http://localhost:8000/owner/add-property"
booking_url = "http://localhost:8000/bookings/Create"

image_pool = [
    "https://plus.unsplash.com/premium_photo-1661964402307-02267d1423f5?q=80",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32?q=80",
    "https://plus.unsplash.com/premium_photo-1675616563084-63d1f129623d?q=80",
    "https://plus.unsplash.com/premium_photo-1661879252375-7c1db1932572?q=80",
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80",
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80",
    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80"
]

locations = [
    "Shimla", "Darjeeling", "Kodaikanal", "Alleppey", "Rishikesh",
    "Ooty", "Lonavala", "Pondicherry", "Coorg", "Mahabaleshwar"
]

property_types = [
    "Cottage", "Bungalow", "Resort", "Lodge", "Homestay",
    "Farmhouse", "Cabin", "Villa", "Retreat", "Inn"
]

user_names = [
    "Rohit Agarwal", "Sneha Kapoor", "Aman Verma", "Isha Rawat",
    "Taranjit Singh", "Riya Das", "Manoj Nair", "Pooja Patel",
    "Deepak Joshi", "Anjali Mehra"
]

review_comments = [
    "Very comfortable stay and great food.",
    "Would definitely recommend to friends.",
    "Clean rooms and friendly staff.",
    "Amazing views and peaceful atmosphere.",
    "Perfect for a weekend getaway.",
    "A hidden gem with amazing scenery.",
    "Rooms were clean and well maintained.",
    "Could improve on service speed.",
    "Excellent hospitality and food.",
    "Perfect blend of nature and comfort."
]

# Create some owners
owners = [
    {"owner_id": f"owner{i}", "name": f"Owner {i}", "property_ids": []}
    for i in range(5)
]

owner_ids = []

for owner in owners:
    try:
        res = requests.post(owner_url, json=owner)
        res.raise_for_status()
        owner_ids.append(owner["owner_id"])
    except Exception as e:
        print(f"Failed to create owner {owner['owner_id']}: {e}")

# Create properties and assign to owners
property_ids = []

for i in range(50):
    location = random.choice(locations)
    ptype = random.choice(property_types)
    pname = f"{location} {ptype} #{i + 1}"

    property_data = {
        "name": pname,
        "location": location,
        "price_per_night": float(random.randint(100, 500)),
        "available": random.choice([True, True, False]),
        "rooms": random.randint(1, 6),
        "images": random.sample(image_pool, k=random.randint(1, 3)),
        "latitude": round(random.uniform(8.0, 34.0), 5),
        "longitude": round(random.uniform(68.0, 85.0), 5),
        "reviews": [
            {
                "user_id": f"user{random.randint(100, 200)}",
                "user_name": random.choice(user_names),
                "rating": random.randint(3, 5),
                "comment": random.choice(review_comments),
                "created_at": str(datetime.now() - timedelta(days=random.randint(0, 365)))
            }
            for _ in range(random.randint(1, 3))
        ]
    }

    try:
        res = requests.post(property_url, json=property_data)
        res.raise_for_status()
        prop_id = res.json()["id"]
        property_ids.append(prop_id)

        # Assign to a random owner
        owner_id = random.choice(owner_ids)
        add_res = requests.post(f"{add_property_url}/{owner_id}/{prop_id}")
        add_res.raise_for_status()

        # Create 1–3 bookings for this property
        for _ in range(random.randint(1, 3)):
            days_ago = random.randint(1, 30)
            stay_length = random.randint(1, 5)
            from_date = datetime.now() - timedelta(days=days_ago)
            to_date = from_date + timedelta(days=stay_length)

            booking_data = {
                "user_id": f"user{random.randint(100, 999)}",
                "property_id": prop_id,
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
                "guests": random.randint(1, 4),
                "status": random.choice(["pending", "accepted", "rejected"]),
                "total_cost": 0  # will be auto-calculated
            }

            bres = requests.post(booking_url, json=booking_data)
            bres.raise_for_status()
        print(f"{i+1}/50 => Created {pname}, assigned to {owner_id}")
    except Exception as e:
        print(f"Error creating property #{i+1}: {e}")