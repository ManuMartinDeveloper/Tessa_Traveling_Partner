# amadeus_api_client.py
#this file contains the AmadeusAPI class to interact with Amadeus APIs for flight and hotel searches. 
#THIS FILE IS WORKING AS OF 19-10-2025

# ---- importing necessary libraries ----
import os
import json
from dotenv import load_dotenv
from datetime import date, timedelta
from amadeus import Client, ResponseError


class AmadeusAPI:
    """
    A client to interact with the Amadeus APIs.
    Handles authentication and provides methods to search for flights and hotels.
    """
    def __init__(self,client_id_user=None,client_secret_user=None):
        """
        Initializes the Amadeus client using credentials from environment variables.
        """
        try:
            # ---- loading environment variables ----
            load_dotenv()

            self.client = Client(
                client_id=os.environ.get("AMADEUS_CLIENT_ID") if os.environ.get("AMADEUS_CLIENT_ID") else client_id_user,
                client_secret=os.environ.get("AMADEUS_CLIENT_SECRET") if os.environ.get("AMADEUS_CLIENT_SECRET") else client_secret_user,
            )
        except Exception as e:
            print(f"🔴 ERROR: Failed to initialize Amadeus client: {e}")
            self.client = None

    def find_one_way_flights(self, origin, destination, departure_date, number_of_adults=1, number_of_children=0, nonstop=True, max_results=10):
        """
        Searches for one-way flights between an origin and destination on a specific date.
        """
        if not self.client:
            return "Amadeus client is not initialized. Check API credentials."
        else:
            print(f"✈️  Searching for flights: {origin} -> {destination} on {departure_date}")
            try:
                response = self.client.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=departure_date,
                    adults=number_of_adults,
                    children=number_of_children,
                    nonStop='true' if nonstop else 'false',
                    max=max_results
                )
                return response.data
            except ResponseError as e:
                print(f"🔴 ERROR: Amadeus flight API call failed: {e}")
                return f"An error occurred while searching for flights: {e.description}"
            except Exception as e:
                print(f"🔴 ERROR: An unexpected error occurred during flight search: {e}")
                return "An unexpected error occurred during the flight search."

    def find_hotels_in_city(self, city_code):
        """
        Searches for hotels within a specific city.

        Args:
            city_code (str): The IATA code for the city (e.g., 'PAR' for Paris).

        Returns:
            list: A list of hotel data, or an error string.
        """
        if not self.client:
            return "Amadeus client is not initialized. Check API credentials."
        
        print(f"🏨 Searching for hotels in city: {city_code}")
        try:
            # This endpoint finds hotels by a city code.
            response = self.client.reference_data.locations.hotels.by_city.get(cityCode=city_code)
            return response.data
        except ResponseError as e:
            print(f"🔴 ERROR: Amadeus hotel API call failed: {e}")
            return f"An error occurred while searching for hotels: {e.description}"
        except Exception as e:
            print(f"🔴 ERROR: An unexpected error occurred during hotel search: {e}")
            return "An unexpected error occurred during the hotel search."
        
    def find_hotels_by_area(self, latitude, longitude, radius= 2):
        """
        Searches for hotel offers within a given radius of a specific lat/long point.

        Args:
            latitude (float): The latitude of the center point.
            longitude (float): The longitude of the center point.
            radius (int): The radius in kilometers (KM).

        Returns:
            list: A list of hotel location, or an error string.
        """
        if not self.client:
            return "Amadeus client is not initialized. Check API credentials."

        print(f"🏨 Searching for hotels near lat:{latitude}, lon:{longitude} within a {radius}KM radius.")
        try:
            # This endpoint searches for available hotel offers in a specific area.
            # response = self.client.shopping.hotel_offers_search.get(
            #     latitude=latitude,
            #     longitude=longitude,
            #     radius=radius,
            #     radiusUnit='KM',
            #     checkInDate=check_in_date,
            #     checkOutDate=check_out_date
            # )
            response = self.client.reference_data.locations.hotels.by_geocode.get(longitude=longitude,latitude=latitude, radius=radius, radiusUnit='KM')

            return response.data
        except ResponseError as e:
            print(f"🔴 ERROR: Amadeus hotel area search API call failed: {e}")
            return f"An error occurred while searching for hotels by area: {e.description}"
        except Exception as e:
            print(f"🔴 ERROR: An unexpected error occurred during hotel area search: {e}")
            return "An unexpected error occurred during the hotel area search."


# Create a singleton instance to be used across the application
amadeus_api_client_object = AmadeusAPI()

# --- Debugging Block ---
# This block allows the file to be run as a standalone script for testing.
if __name__ == "__main__":
    print("--- Running amadeus_client.py in standalone debug mode ---")
    
    # Load environment variables from a .env file in the root directory
    load_dotenv()

    # Check for necessary API keys
    if not os.environ.get("AMADEUS_CLIENT_ID") or not os.environ.get("AMADEUS_CLIENT_SECRET"):
        print("🔴 FATAL: AMADEUS API keys not found in .env file. Please set them up to run tests.")
    else:
        # Create an instance of the API client
        

        # --- Test Case 1: Search for Flights ---
        print("\n--- Testing Flight Search ---")
        # Set a departure date for one week from today for the test
        test_departure_date = (date.today() + timedelta(days=7)).isoformat()
        flights = amadeus_api_client_object.find_one_way_flights(
            origin="BLR",         # Delhi
            destination="COK",    # Cochin
            departure_date=test_departure_date
        )
        print("--- Flight Results ---")
        if isinstance(flights, list):
            # Pretty print the JSON response
            # print(json.dumps(flights, indent=2))
            output_filename = "flights_output.json"
            with open(output_filename, "w") as f:
                json.dump(flights, f, indent=2)
            print(f"✅ Successfully saved flight results to {output_filename}")
        else:
            print(flights) # Print the error message

        # --- Test Case 2: Search for Hotels ---
        # print("\n--- Testing Hotel Search ---")
        # hotels = client.find_hotels_in_city(city_code="PAR") # Paris
        # print("--- Hotel Results ---")
        # if isinstance(hotels, list):
        #     # Pretty print the JSON response
        #     # print(json.dumps(hotels, indent=2))
        #     output_filename = "hotels_output.json"
        #     with open(output_filename, "w") as f:
        #         json.dump(hotels, f, indent=2)
        #     print(f"✅ Successfully saved hotel results to {output_filename}")
        # else:
        #     print(hotels) # Print the error message

        #  # --- Test Case 3: Search for Hotels by Area ---
        # print("\n--- Testing Hotel Search by Area ---")
        # # Coordinates for the Eiffel Tower
        # eiffel_tower_lat = 48.8584
        # eiffel_tower_lon = 2.2945
        # # Define check-in and check-out dates for the test
        # test_check_in_date = (date.today() + timedelta(days=14)).isoformat()
        # test_check_out_date = (date.today() + timedelta(days=15)).isoformat()
        
        # hotels_area = client.find_hotels_by_area(
        #     latitude=eiffel_tower_lat,
        #     longitude=eiffel_tower_lon,
        #     radius=2, # Search within a 2 KM radius
        #     check_in_date=test_check_in_date,
        #     check_out_date=test_check_out_date
        # )
        # print("--- Hotel by Area Results ---")
        # if isinstance(hotels_area, list):
        #     output_filename = "hotels_by_area_output.json"
        #     with open(output_filename, "w") as f:
        #         json.dump(hotels_area, f, indent=2)
        #     print(f"✅ Successfully saved hotel area results to {output_filename}")
        # else:
        #     print(hotels_area)
