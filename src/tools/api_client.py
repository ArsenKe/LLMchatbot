import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv
import json

# Configure logging
logger = logging.getLogger(__name__)

class BookingAPIClient:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://api.makcorps.com/city"
        self.api_key = os.getenv("MAKCORPS_API_KEY")
        self.use_simulation = os.getenv("USE_SIMULATION", "false").lower() == "true"
        
        if not self.api_key and not self.use_simulation:
            logger.warning("MakCorps API key missing. Falling back to simulation mode")
            self.use_simulation = True

    def search_hotels(
        self,
        location: str,
        checkin_date: str,
        checkout_date: Optional[str] = None,
        guest_count: int = 2
    ) -> Dict[str, Any]:
        """Search hotels using MakCorps API with robust error handling"""
        if self.use_simulation:
            return self._get_simulated_data(location, checkin_date)
        
        # Extract city ID from location string
        city_id = self._extract_city_id(location)
        checkout = checkout_date or self._calculate_checkout(checkin_date)
        
        params = {
            "api_key": self.api_key,
            "cityid": city_id,
            "checkin": checkin_date,
            "checkout": checkout,
            "adults": guest_count
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            return self._format_response(response.json(), location, checkin_date, checkout)
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return self._get_simulated_data(location, checkin_date)
        except (ValueError, KeyError) as e:
            logger.error(f"Response parsing failed: {e}")
            return {
                "status": "error",
                "message": "Failed to parse hotel data"
            }

    def _extract_city_id(self, location: str) -> str:
        """Extract city ID from location string if available"""
        if "(" in location and ")" in location:
            return location.split("(")[-1].split(")")[0].strip()
        return location

    def _calculate_checkout(self, checkin_date: str) -> str:
        """Calculate checkout date (1 day after checkin)"""
        return (datetime.strptime(checkin_date, "%Y-%m-%d") + 
                timedelta(days=1)).strftime("%Y-%m-%d")

    def _get_simulated_data(self, location: str, checkin_date: str) -> Dict[str, Any]:
        """Return simulated hotel data for testing"""
        checkout_date = self._calculate_checkout(checkin_date)
        return {
            "status": "success",
            "hotels": [
                {
                    "id": "sim_001",
                    "name": f"Luxury Hotel in {location}",
                    "rating": 4.8,
                    "price": 250,
                    "currency": "EUR",
                    "location": location,
                    "checkin": checkin_date,
                    "checkout": checkout_date,
                    "url": "https://example.com/hotel1"
                },
                {
                    "id": "sim_002",
                    "name": f"Boutique Hotel in {location}",
                    "rating": 4.5,
                    "price": 180,
                    "currency": "EUR",
                    "location": location,
                    "checkin": checkin_date,
                    "checkout": checkout_date,
                    "url": "https://example.com/hotel2"
                }
            ]
        }
    
    def _format_response(self, data: List[Dict[str, Any]], 
                        location: str, 
                        checkin: str, 
                        checkout: str) -> Dict[str, Any]:
        """Standardize API response format"""
        hotels = []
        for hotel in data:
            # Skip invalid entries
            if not isinstance(hotel, dict):
                continue
                
            hotels.append({
                "id": hotel.get("id", ""),
                "name": hotel.get("name", "Unknown Hotel"),
                "rating": hotel.get("rating", hotel.get("reviews", {}).get("rating", 0)),
                "price": hotel.get("price", 0),
                "currency": hotel.get("currency", "EUR"),
                "location": location,
                "checkin": checkin,
                "checkout": checkout,
                "url": hotel.get("url", "")
            })
        
        return {
            "status": "success",
            "location": location,
            "checkin": checkin,
            "checkout": checkout,
            "hotels": hotels
        }