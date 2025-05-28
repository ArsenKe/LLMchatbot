import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class BookingAPIClient:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://api.makcorps.com/city"  # Updated endpoint
        self.api_key = os.getenv("MAKCORPS_API_KEY")
        self.use_simulation = os.getenv("USE_SIMULATION", "true").lower() == "true"

    def get_hotels(
        self,
        location: str,
        checkin_date: str,
        checkout_date: Optional[str] = None,
        guest_count: int = 2
    ) -> Dict[str, Any]:
        """Search for hotels using MakCorps API"""
        
        if self.use_simulation:
            return self._get_simulated_data(location, checkin_date)
            
        # Extract city ID if provided in format "City (ID)"
        city_id = location.split("(")[-1].strip(")") if "(" in location else location
        
        # Prepare request data
        data = {
            "api_key": self.api_key,
            "cityid": city_id,
            "checkin": checkin_date,
            "checkout": checkout_date or (
                datetime.strptime(checkin_date, "%Y-%m-%d") + 
                timedelta(days=1)
            ).strftime("%Y-%m-%d"),
            "adults": guest_count
        }
        
        try:
            # Try POST request first
            response = requests.post(
                self.base_url,
                json=data,
                timeout=10
            )
            
            # Log response for debugging
            logger.debug(f"Status Code: {response.status_code}")
            logger.debug(f"Response Text: {response.text}")
            
            response.raise_for_status()
            return self._format_response(response.json())
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if self.use_simulation:
                return self._get_simulated_data(location, checkin_date)
            return {
                "status": "error",
                "message": f"API request failed: {str(e)}"
            }
    
    def _get_simulated_data(self, location: str, checkin_date: str) -> Dict[str, Any]:
        """Return simulated hotel data for testing"""
        return {
            "status": "success",
            "hotels": [
                {
                    "name": f"Luxury Hotel in {location}",
                    "price_booking": "$250",
                    "price_expedia": "$245",
                    "price_hotels": "$255",
                    "rating": 4.8,
                    "city_id": "12345"
                },
                {
                    "name": f"Boutique Hotel in {location}",
                    "price_booking": "$180",
                    "price_expedia": "$175",
                    "price_hotels": "$185",
                    "rating": 4.5,
                    "city_id": "12345"
                }
            ],
            "location": location,
            "dates": {
                "checkin": checkin_date,
                "checkout": (
                    datetime.strptime(checkin_date, "%Y-%m-%d") + 
                    timedelta(days=1)
                ).strftime("%Y-%m-%d")
            }
        }
    
    def _format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format API response with consistent price data"""
        hotels = []
        for hotel in data.get("hotels", []):
            # Extract prices from various fields
            prices = []
            
            # Handle direct price field
            if "price" in hotel:
                if isinstance(hotel["price"], dict):
                    amount = hotel["price"].get("amount")
                    currency = hotel["price"].get("currency", "USD")
                    if amount:
                        prices.append(f"Base Price: {amount} {currency}")
                elif hotel["price"]:
                    prices.append(f"Base Price: {hotel['price']}")
            
            # Handle vendor-specific prices
            for key, value in hotel.items():
                if key.startswith("price_") and value:
                    vendor = key.replace("price_", "").title()
                    prices.append(f"{vendor}: {value}")
            
            # Create formatted hotel entry
            hotels.append({
                "name": hotel.get("name", "Unknown Hotel"),
                "rating": hotel.get("rating", "N/A"),
                "prices": prices or ["Price information not available"],
                "location": data.get("location", "Unknown Location"),
                "dates": data.get("dates", {})
            })
        
        return {
            "status": "success",
            "hotels": hotels,
            "total_found": len(hotels)
        }