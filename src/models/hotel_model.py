from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date

class HotelSearchRequest(BaseModel):
    """Request model for hotel searches"""
    location: str
    checkin_date: date
    checkout_date: Optional[date] = None
    guest_count: int = 2
    currency: str = "EUR"

class PriceInfo(BaseModel):
    """Detailed price information"""
    amount: float
    currency: str
    source: str  # e.g., "MakCorps", "Booking.com"

class HotelDetails(BaseModel):
    """Detailed hotel information"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    name: str
    rating: Optional[float] = None
    description: Optional[str] = None
    amenities: List[str] = []
    prices: List[PriceInfo] = []
    location: str
    checkin_date: date
    checkout_date: date
    image_url: Optional[str] = None
    booking_url: str

class HotelSearchResponse(BaseModel):
    """Standardized hotel search response"""
    status: str  # "success" or "error"
    location: str
    checkin_date: date
    checkout_date: date
    hotels: List[HotelDetails]
    message: Optional[str] = None  # For error messages