import httpx

base_url = "http://192.168.1.41:8000/filtered-wfs"

params = {
    "country": "malta",
    # "bbox": "16.3,48.1,16.5,48.3",
    "cql_filter": "area > 12500",
    "maxfeatures": 100,
}

response = httpx.get(base_url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Received {len(data['features'])} features")
else:
    print(f"Error {response.status_code}: {response.text}")
