from fastapi import FastAPI
from app.routes import properties, bookings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(properties.router)
app.include_router(bookings.router)

app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # or ["*"] for all origins (dev only)
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )