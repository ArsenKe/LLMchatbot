import re
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any

class TourismAgent:
    def __init__(self, llm_client, hotel_api):
        self.llm = llm_client
        self.hotel_api = hotel_api

    def classify_intent(self, message: str) -> str:
        message = message.lower()
        hotel_keywords = ["hotel", "stay", "accommodation", "book", "reservation"]
        if any(kw in message for kw in hotel_keywords):
            return "hotel_search"
        return "general_question"

    def extract_parameters(self, message: str) -> Tuple[str, str]:
        location = "Vienna"
        if " in " in message:
            location = message.split(" in ")[-1].split(" for ")[0].strip()
        today = datetime.now()
        if "tomorrow" in message:
            date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in message:
            date = (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
        else:
            days_until_saturday = (5 - today.weekday() + 7) % 7
            date = (today + timedelta(days=days_until_saturday)).strftime("%Y-%m-%d")
        return location, date

    def search_hotels(self, location: str, date: str) -> List[Dict[str, Any]]:
        # Replace with your real hotel API call if available
        return [
            {
                "name": f"Grand {location} Hotel",
                "price": "$150/night",
                "rating": 4.5,
                "location": f"Central {location}",
                "url": f"https://example.com/hotels/grand-{location.lower()}"
            },
            {
                "name": f"{location} Riverside Inn",
                "price": "$120/night",
                "rating": 4.2,
                "location": f"Riverside, {location}",
                "url": f"https://example.com/hotels/{location.lower()}-riverside"
            }
        ]

    def generate_response(self, hotels: List[Dict[str, Any]]) -> str:
        if not hotels:
            return "I couldn't find any hotels matching your criteria."
        prompt = (
            "You are a helpful travel assistant. Summarize these hotel options "
            "in a friendly, concise way:\n\n"
            + "\n".join([f"- {h['name']} ({h['price']}, Rating: {h['rating']}/5)" for h in hotels])
        )
        return self.llm.text_generation(
            prompt,
            max_new_tokens=200,
            temperature=0.7
        )

    def process_message(self, message: str) -> dict:
        intent = self.classify_intent(message)
        if intent == "hotel_search":
            location, date = self.extract_parameters(message)
            hotels = self.search_hotels(location, date)
            response = self.generate_response(hotels)
            return {
                "response": response,
                "hotels": hotels
            }
        else:
            prompt = (
                "You are a helpful travel assistant. Answer this question "
                f"in a friendly, informative way:\n\n{message}"
            )
            return {
                "response": self.llm.text_generation(prompt, max_new_tokens=200),
                "hotels": []
            }