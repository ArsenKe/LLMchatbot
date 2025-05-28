from langchain.tools import Tool
from .api_client import BookingAPIClient

class TourismTools:
    def __init__(self):
        self.client = BookingAPIClient()

    def search_hotels(self, location: str, checkin_date: str, checkout_date: str=None):
        return self.client.get_hotels(location, checkin_date, checkout_date)

hotel_tool = Tool(
    name="search_hotels",
    description="Search for hotels in a city given its ID and dates",
    func=TourismTools().search_hotels
)
