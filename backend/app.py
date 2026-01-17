import pandas as pd
import pickle
import bz2
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # This loads the .env file
CORS(app)  # Allow React to talk to this server

# --- CONFIGURATION ---
# 🔴 REPLACE THIS WITH YOUR ACTUAL TMDB API KEY
API_KEY = os.getenv("TMDB_API_KEY")

# --- LOAD DATA (With Error Handling) ---
print("Loading model files...")
try:
    # Load compressed files to save space
    movies_dict = pickle.load(bz2.open('movie_dict.pbz2', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(bz2.open('similarity.pbz2', 'rb'))
    print("Model loaded successfully!")
except FileNotFoundError:
    print("ERROR: .pbz2 files not found! Did you run compress_data.py?")
    movies = None
    similarity = None

# --- HELPER: FETCH POSTER FROM TMDB ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        # Timeout ensures the server doesn't hang if TMDB is slow
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://placehold.co/500x750?text=No+Image"
    except Exception as e:
        # If API fails (e.g. connection error), return placeholder
        return "https://placehold.co/500x750?text=Error"

# --- CORE LOGIC: RECOMMENDATION ---
def get_recommendations(movie_title):
    # 1. robust search (lowercase to avoid casing issues)
    movie_title = movie_title.lower()
    matches = movies[movies['title'].str.lower() == movie_title]
    
    if matches.empty:
        return []

    # 2. Mathematical Similarity
    idx = matches.index[0]
    distances = similarity[idx]
    
    # Get top 5 matches (excluding the movie itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        # 3. Fetch Poster (Server-Side)
        poster_url = fetch_poster(movie_id)
        
        recommended_movies.append({
            "title": movies.iloc[i[0]].title,
            "poster": poster_url,
            "id": str(movie_id)
        })
        
    return recommended_movies

# --- API ROUTES ---
@app.route('/recommend', methods=['POST'])
def recommend():
    if movies is None:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.get_json()
    movie_title = data.get('movie')
    
    print(f"Request received for: {movie_title}") # Debug log

    if not movie_title:
        return jsonify({"error": "Please provide a movie name"}), 400

    recommendations = get_recommendations(movie_title)
    
    if not recommendations:
        return jsonify({"error": "Movie not found! Try 'Batman' or 'Avatar'."}), 404

    return jsonify(recommendations)

@app.route('/')
def home():
    return "Backend is Live & Running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)