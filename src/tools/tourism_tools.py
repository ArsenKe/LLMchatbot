from langchain.tools import tool
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def search_hotels(location: str, checkin_date: str) -> str:
    """Search hotels using MakCorps API"""
    try:
        # Extract city ID if provided in format "New York (60763)"
        city_id = location
        if "(" in location and ")" in location:
            city_id = location.split("(")[1].split(")")[0].strip()
        
        # Prepare API request
        params = {
            "api_key": os.getenv("MAKCORPS_API_KEY"),
            "cityid": city_id,
            "checkin": checkin_date,
            "adults": 2
        }
        
        # API call with timeout
        response = requests.get(
            "https://api.makcorps.com/city",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Format first 3 results
        hotels = []
        for hotel in data[:3]:
            name = hotel.get('name', 'Unknown Hotel')
            rating = hotel.get('reviews', {}).get('rating', 'N/A')
            prices = [f"${hotel.get(f'price{i}', '?')}" for i in range(1,5) 
                     if hotel.get(f'price{i}')]
            
            hotel_info = [
                f"🏨 {name}",
                f"⭐ Rating: {rating}",
                f"💵 Prices: {', '.join(prices)}"
            ]
            hotels.append("\n".join(hotel_info))
        
        return "\n\n".join(hotels) if hotels else "No hotels found"
            
    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        return "Couldn't retrieve hotels. Please try different parameters."

# Export tool
hotel_tool = search_hotels