import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
from flask import Flask
from flask import render_template, url_for, request, redirect
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
def recommender(movie_name):
    movies_df = pd.read_csv('movies.csv')
    features = ['genres','keywords', 'tagline','cast','director']

    for col in features:
        movies_df[col] = movies_df[col].fillna('')

    joined_features = movies_df['genres']+' '+movies_df['keywords']+' '+movies_df['tagline']+' '+movies_df['cast']+' '+movies_df['director']
    vectorizer = TfidfVectorizer()
    feature_vectors = vectorizer.fit_transform(joined_features)
    similarity = cosine_similarity(feature_vectors)
    list_titles = movies_df['title'].tolist()
    
    find_title_match = difflib.get_close_matches(movie_name.lower(),list_titles)
    title_match = find_title_match[0]
    
    index_movie = movies_df[movies_df['title'] == title_match]['index'].values[0]
    similarity_movies = list(enumerate(similarity[index_movie]))
    sorted_similarity = sorted(similarity_movies,key = lambda x:x[1],reverse = True)
    related_movies = list(i[0] for i in sorted_similarity)[1:10]
    recommended_movies = list(movies_df[movies_df.index == index]['title'].values[0] for index in related_movies)
    # for index in related_movies:
    #     recommended_movies = movies_df['title']
    # print(recommended_movies)
    return recommended_movies

def links(movie_name):
    movie_contents = requests.get('https://www6.f2movies.to/search/'+movie_name)
    # print(movie_contents.text)
    soup = BeautifulSoup(movie_contents.text,'html.parser')
    link = soup.find_all('a',{'href':True})
    # print(link)
    for tag in link:
        if '/movie/' in tag['href']:
            return tag['href']


@app.route("/",methods=["GET","POST"])
def GUI():
    if request.method=="POST":
        movie_name = request.form["movie"]
        try:
            movies = recommender(movie_name)
            for movie in movies:
                movie_link = links(movie.replace(' ','-'))
                if movie_link!=None:
                    print(movie+"- "+"https://www6.f2movies.to"+movie_link)
        except:
            print("Please enter different movie name")
        return redirect(request.url)
    return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)