from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests

# Initialize the Flask app
app = Flask(__name__)


# Function to fetch movie poster from OMDb API
def fetch_poster(movie_title):
    api_key = "e9f123d2"
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url).json()
    if "Poster" in response and response["Poster"] != "N/A":
        return response["Poster"]
    return None


# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    recommended_posters = []

    for i in distances[1:6]:  # Fetching top 5 recommendations
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))

    return recommended_movies, recommended_posters


# Load data
movie_list = pickle.load(open('movie_list.pkl', 'rb'))
movies = pd.DataFrame(movie_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_list = movie_list['title'].values


# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html', movie_list=movie_list)


# Route to handle movie recommendations
@app.route('/recommend', methods=['POST'])
def recommend_movies():
    selected_movie_name = request.form['movie_name']
    recommendations, posters = recommend(selected_movie_name)

    # Display recommendations in 5 columns
    recommendations_html = []
    for idx, (movie, poster) in enumerate(zip(recommendations, posters)):
        if poster:
            recommendations_html.append(f"""
                <div style="text-align: center;">
                    <p>{movie}</p>
                    <img src="{poster}" width="150" alt="{movie}">
                </div>
            """)
        else:
            recommendations_html.append(f"<p>{movie} - Poster not available</p>")

    return render_template('recommendation.html', recommendations=recommendations_html)


if __name__ == '__main__':
    app.run(debug=True)
