from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class HotelSearchConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    location: str
    checkin_date: str
    checkout_date: Optional[str] = None
    guest_count: int = 2

class PriceInfo(BaseModel):
    amount: Optional[float] = None
    currency: str = "USD"

class HotelData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    rating: Optional[float] = None
    prices: List[str] = []
    location: Optional[str] = None
    dates: Dict[str, Any] = {}