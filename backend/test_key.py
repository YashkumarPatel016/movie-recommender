import requests

API_KEY = "PASTE_YOUR_KEY_HERE"
url = f"https://api.themoviedb.org/3/movie/550?api_key={API_KEY}"

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! TMDB is accessible.")
    else:
        print("Error: Invalid Key or blocked.")
except Exception as e:
    print(f"Connection Failed: {e}")