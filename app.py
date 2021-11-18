# AS simeple as possbile flask google oAuth 2.0
from flask import Flask, redirect, url_for, session,render_template,request
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D


# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required

# dotenv setup
from dotenv import load_dotenv
load_dotenv()


# App config
app = Flask(__name__)
# Session config
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

def cluster(df, col):
    data = pd.DataFrame()
    for j in col:
        data[j]=df[j]
    cluster_n =silhoutte(data)
    km = KMeans(n_clusters=cluster_n)
    clusters = km.fit_predict(data)
    df["label"] = clusters
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(111, projection='3d')
    colors = ['blue','red','yellow','orange','green','purple']
    count = 0
    for i in range(cluster_n):
        ax.scatter(df[col[0]][df.label == i], df[col[1]][df.label == i], df[col[2]][df.label == i], c=colors[count], s=60)
        count+=1
    ax.view_init(30, 185)
    plt.xlabel(col[0])
    plt.ylabel(col[1])
    ax.set_zlabel(col[2])
    plt.show()
    image_path = os.path('image'+'.png')
    plt.savefig(image_path)

def silhoutte(data):
    km_silhouette = []
    for k in range(2,11):
        kmeans = KMeans(n_clusters=k, init="k-means++")
        kmeans.fit(data)
        preds = kmeans.predict(data)    
        silhouette = silhouette_score(data,preds)
        km_silhouette.append(silhouette)
    cluster_n = int(km_silhouette.index(max(km_silhouette)))+1
    return cluster_n

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/home', methods =['GET','POST'])
@login_required
def home():
    email = dict(session)['profile']['email']
    if request.method == 'POST':
        file = pd.read_csv(request.files['file'])
        col =['CustomerID','Age','Income']
        cluster(file,col)
    return render_template('index.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/home')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
