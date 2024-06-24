import requests
from pprint import pprint
import os

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

session = requests.Session()
session.headers['Authorization'] = f"ApiKey {os.environ.get('OPENSANCTIONS_API_KEY')}"

def get_sanction_data(business_name, jurisdiction):
     URL = "https://api.opensanctions.org/match/sanctions?algorithm=best"

     # Create the query for the company
     query = {
          "schema": "Company",
          "properties": {
               "name": [business_name],
               "jurisdiction": [jurisdiction],
          },
     }

     # Put the query into a matching batch
     BATCH = {"queries": {"q1": query}}

     # Configure the scoring system
     PARAMS = {"algorithm": "best", "fuzzy": "false"}

     # Send the batch off to the API and raise an exception for a non-OK response code
     response = session.post(URL, json=BATCH, params=PARAMS)
     response.raise_for_status()

     responses = response.json().get("responses")
     results = responses.get("q1").get("results")


     # Find the object with match True and highest score
     best_match = None
     highest_score = 0.0

     for result in results:
          if  result.get('match') and result.get('score', 0) > highest_score:
               best_match = result
               highest_score = result.get('score', 0)

     # Return the best match if found, otherwise return an empty list
     return best_match if best_match else None

print(get_sanction_data("airbnb", "united states"))