import requests # type: ignore
from datetime import datetime, timedelta
import random

url = "http://localhost:8000/properties/"

# Reusable image pool from existing properties
image_pool = [
    "https://plus.unsplash.com/premium_photo-1661964402307-02267d1423f5?q=80&w=1073&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://plus.unsplash.com/premium_photo-1675616563084-63d1f129623d?q=80&w=1169&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://plus.unsplash.com/premium_photo-1661879252375-7c1db1932572?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
]

locations = ["Shimla", "Darjeeling", "Kodaikanal", "Alleppey", "Rishikesh", "Ooty", "Lonavala", "Pondicherry", "Coorg", "Mahabaleshwar"]
property_types = ["Cottage", "Bungalow", "Resort", "Lodge", "Homestay", "Farmhouse", "Cabin", "Villa", "Retreat", "Inn"]
user_names = ["Rohit Agarwal", "Sneha Kapoor", "Aman Verma", "Isha Rawat", "Taranjit Singh", "Riya Das", "Manoj Nair", "Pooja Patel"]
review_comments = [
    "Very comfortable stay and great food.",
    "Would definitely recommend to friends.",
    "Clean rooms and friendly staff.",
    "Amazing views and peaceful atmosphere.",
    "Perfect for a weekend getaway."
]

for i in range(50):
    property_data = {
        "name": f"{random.choice(locations)} {random.choice(property_types)} {i+1}",
        "location": random.choice(locations),
        "price_per_night": float(random.randint(70, 200)),
        "available": random.choice([True, False]),
        "rooms": random.randint(1, 5),
        "images": [random.choice(image_pool)],
        "latitude": round(random.uniform(8.0, 34.0), 4),
        "longitude": round(random.uniform(68.0, 85.0), 4),
        "reviews": [
            {
                "user_id": f"user{i+100}",
                "user_name": random.choice(user_names),
                "rating": random.randint(3, 5),
                "comment": random.choice(review_comments),
                "created_at": str(datetime.now() - timedelta(days=random.randint(1, 100)))
            }
        ]
    }

    response = requests.post(url, json=property_data)
    print(f"{i+1}/50 => Status: {response.status_code}, Property: {property_data['name']}")
