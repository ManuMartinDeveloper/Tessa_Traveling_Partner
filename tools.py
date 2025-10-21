from typing import Optional
from langchain.tools import tool
from datetime import date
from geopy.geocoders import Nominatim
from amadeus_api_client import amadeus_api_client_object as amadeus_client

from pydantic import BaseModel, Field

class FlightSearchInput(BaseModel):
    """
    Defines the arguments for the flight search tool.
    """
    # --- REQUIRED ARGUMENTS ---
    origin: str = Field(..., # The '...' means this field is required
        description="The 3-letter IATA airport code for the origin city. Example: 'BLR' for Bengaluru.")
    
    destination: str = Field(..., description="The 3-letter IATA airport code for the destination city. Example: 'DXB' for Dubai.")
    departure_date: str = Field(..., description="The single departure date, formatted as YYYY-MM-DD.")

    # --- OPTIONAL ARGUMENTS (with defaults) ---
    num_adults: int = Field(default=1, description="The total number of adult passengers. Defaults to 1 if not specified by the user.")
    num_children: int = Field(default=0, description="The total number of child passengers. Defaults to 0 if not specified by the user.")
    non_stop: bool = Field(default=True, description="Whether the user wants a non-stop flight. Set to True unless the user explicitly asks for layovers.")
    maximum_results: int = Field(default=10, description="The maximum number of flight results to return. Defaults to 10.")

class HotelCitySearchInput(BaseModel):
    """Input schema for the search_hotels tool."""
    city_code: str = Field(..., description="The IATA code for the city where to search for hotels (e.g., 'PAR' for Paris).")

class HotelAreaSearchInput(BaseModel):
    """Input schema for the search_hotels_by_area tool."""
    place_name: Optional[str] = Field(None, 
        description="The name of the location or area (e.g., 'Eiffel Tower, Paris') for the hotel search."
    )
    latitude: Optional[float] = Field(None, description="The latitude of the center point for the hotel search.")
    longitude: Optional[float] = Field(None, description="The longitude of the center point for the hotel search.")
    radius: int = Field(default=2, description="The radius in kilometers (KM) for the search area.")

    # check_in_date: str = Field(description="The check-in date for the hotel stay, formatted as YYYY-MM-DD.")
    # check_out_date: str = Field(description="The check-out date for the hotel stay, formatted as YYYY-MM-DD.")

def _get_geocoordinates(address: str) -> Optional[tuple]:
    """
    Uses geopy to convert an address into latitude and longitude coordinates.

    Args:
        address (str): The address or landmark to geocode.

    Returns:
        tuple: A tuple containing (latitude, longitude) if found, else None.
    """

    geolocator = Nominatim(user_agent="TravelAgentApp")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"🔴 ERROR: Could not geocode the address: {address}")
        return None

# --- Tool Definitions ---
@tool
def get_current_date() -> str:
    """
    Returns the current date. Use this tool to resolve relative date queries
    like 'today', 'tomorrow', or 'next Tuesday'. The query parameter is not used.
    """
    print("📅 Getting the current date...")
    return date.today().strftime("%Y-%m-%d")

@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, departure_date: str, num_adults: str = 1, num_children: str = 0, non_stop: bool = True, maximum_results: int = 10) -> list:
    """
    Searches for one-way flights based on the user's criteria.
    You MUST provide origin, destination, and departure_date.
    """
    print(f"✈️ Searching for flights from {origin} to {destination} on {departure_date}...")
    print(f"    Adults: {num_adults}, Children: {num_children}, Non-stop: {non_stop}, Max Results: {maximum_results}")
    response = amadeus_client.find_one_way_flights(origin= origin, destination= destination, departure_date= departure_date, number_of_adults= num_adults, number_of_children= num_children, nonstop= non_stop, max_results= maximum_results)
    print(f"    Found {len(response)} flights. \n flight details: {response}")
    return response

@tool(args_schema=HotelCitySearchInput)
def search_hotels_by_city(city_code: str) -> list:
    """Searches for hotels in a given city by its IATA code."""
    print(f"🏨 Searching for hotels in city: {city_code}...")
    return amadeus_client.find_hotels_in_city(city_code)

@tool(args_schema=HotelAreaSearchInput)
def search_hotels_by_area(place_name: str = None,latitude: float = None, longitude: float = None, radius: int=2) -> list:
    """
    Searches for available hotel offers within a specific radius of a geographic coordinate or place name.
    Use this when a user wants to find hotels near a specific landmark or address.
    """
    if place_name and (longitude is None and latitude is None):
        print(f"📍 Geocoding place name: {place_name}...")
        coordinates = _get_geocoordinates(place_name)
        if coordinates:
            latitude, longitude = coordinates
            print(f"Geocoding successful: ({latitude}, {longitude})")
        else:
            # 4. Return a clear error message if geocoding failed
            print(f"Geocoding failed for: {place_name}")
            return f"Error: Could not find the coordinates for the location '{place_name}'. Please try a different or more specific landmark."
    
    if latitude is None or longitude is None:
        return "Error: Cannot search for hotels without a valid location. Please provide a place_name or valid latitude/longitude."

    print(f"🏨 Searching for hotels near ({latitude}, {longitude}) within {radius}KM...")
    return amadeus_client.find_hotels_by_area(latitude, longitude, radius)


# --- List of all available tools for the agent ---
available_tools = [
    get_current_date,
    search_flights,
    search_hotels_by_city,
    search_hotels_by_area,
]

