from fastapi import FastAPI
from app.routes import properties, bookings, owners
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(properties.router)
app.include_router(bookings.router)
app.include_router(owners.router)  

app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )