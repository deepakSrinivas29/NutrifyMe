import http.client
import json

headers = {
    "x-app-id": "310f582a",
    "x-app-key": "1ccd7b3fbdeae869fe5b10c863614137",
    "x-remote-user-id": 0,
}


# "Content-type": "application/json"

def fetch_calories(food_name):
    payload = {"query": food_name}

    conn = http.client.HTTPSConnection("trackapi.nutritionix.com")

    conn.request("POST", "/v2/natural/nutrients", json.dumps(payload), headers)

    response = conn.getresponse().read()
    data = json.loads(response)
    return data['foods'][0]["nf_calories"]
