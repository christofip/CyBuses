import requests
from google.transit import gtfs_realtime_pb2

# API URL
url = "http://20.19.98.194:8328/Api/api/gtfs-realtime"

# Fetch the data
response = requests.get(url)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

# Print feed in JSON-like structure
for entity in feed.entity:
    print(entity)
