from dotenv import load_dotenv
from flask import Flask, request
# from flask_smorest import Blueprint, abort
import os
import base64
import json
from requests import get
import requests
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


# engine = create_engine('sqlite:///mydatabase.db', echo=True)

# Base = declarative_base()


# # app = Flask(__name__)

# load_dotenv()

# # client_id = os.getenv("CLIENT_ID")
# # client_secret = os.getenv("CLIENT_SECRET")



def get_token():
    client_id = '3431746dc9b34936b0ebfe7311f00b6c'
    client_secret = '682fd8dca0c24101a1ef26fd846a843e'

    
    # Define the data you need to send in the POST request
    # data = {
    #     'grant_type': 'authorization_code',  # Specify the grant type
    #     'code': request.form.get('code'),  # Get the code from the request
    #     'redirect_uri': 'http://your-redirect-uri.com',  # Replace with your actual redirect URI
    # }
    data = {"grant_type" : "client_credentials"}

    # Define the headers for the request, including Authorization
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Send the POST request to obtain the access token
    #response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        # Do something with the access token
        #return f'Access Token: {access_token}'
        return access_token
    else:
        return 'Failed to obtain access token'

def get_auth_header(token):
    return {"Authorization": "Bearer " + token }



def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    responde = get(query_url, headers=headers)
    result = responde.json()["artists"]["items"]
    return result[0]

def get_songs_by_artist(token,artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=TR"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    result = response.json()["tracks"]
    return result

def search_for_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    query_url = url + query
    responde = get(query_url, headers=headers)
    result = responde.json()["tracks"]["items"]
    return result[0]


#STARTING POINT FOR DATABASE

# rates_association = Table(
#     'rates_association',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id')),
#     Column('track_id', Integer, ForeignKey('tracks.id')),
#     Column('rating', Integer)
# )


# track_artist_association= Table(
#     'track_artist_association',
#     Base.metadata,
#     Column('artist_id', Integer, ForeignKey('artists.id')),
#     Column('track_id', Integer, ForeignKey('tracks.id'))
# )

# track_album_association= Table(
#     'track_album_association',
#     Base.metadata,
#     Column('album_id', Integer, ForeignKey('albums.id')),
#     Column('track_id', Integer, ForeignKey('tracks.id'))
# )



# likes_tracks_association = Table(
#     'likes_track_association',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id')),
#     Column('track_id', Integer, ForeignKey('tracks.id'))
# )

# likes_artists_association = Table(
#     'likes_artists_association',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id')),
#     Column('artist_id', Integer, ForeignKey('artists.id'))
# )
# likes_albums_association = Table(
#     'likes_albums_association',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id')),
#     Column('album_id', Integer, ForeignKey('albums.id'))
# )

# class Track(Base):
#     __tablename__ = 'tracks'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     # S_id = Column(String, unique = True)
#     duration_ms = Column(Integer)

#     liked_by_users = relationship("User", secondary= likes_tracks_association, back_populates="liked_tracks")

#     artists = relationship("Artist", secondary= track_artist_association, back_populates="tracks")

#     albums = relationship("Album", secondary= track_album_association, back_populates="tracks")

#     rated_by_users = relationship("User", secondary=rates_association, back_populates = "rated_tracks")

    

# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     email = Column(String, unique=True)  
#     password = Column(String)
#     username = Column(String, unique=True)  
#     profile_picture = Column(LargeBinary, nullable=True)  # Binary data for storing images

#     liked_tracks = relationship("Track", secondary= likes_tracks_association, back_populates="liked_by_users")

#     liked_artists = relationship("Artist", secondary=likes_artists_association, back_populates="liked_by_users")

#     liked_albums = relationship("Album", secondary=likes_albums_association, back_populates="liked_by_users")

#     rated_tracks = relationship("Track", secondary = rates_association, back_populates= "rated_by_users")

# class Artist(Base):
#     __tablename__ = 'artists'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     # s_id = Column(String, unique=True)
#     # genres = Column(String)  

#     liked_by_users = relationship("User", secondary=likes_artists_association, back_populates="liked_artists")

#     tracks = relationship("Track",secondary = track_artist_association, back_populates= "artists")

#     # tracks = relationship("Track", back_populates="artist")

#     albums = relationship("Album", back_populates="artist")
    

# class Album(Base):
#     __tablename__ = 'albums'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     # s_id = Column(String, unique=True)  
#     release_date = Column(String)
#     total_tracks = Column(Integer)

#     liked_by_users = relationship("User", secondary=likes_albums_association, back_populates="liked_albums")

#     tracks = relationship("Track", secondary= track_album_association, back_populates="albums")

#     # tracks = relationship("Track", back_populates="album")

#     artist_id = Column(Integer, ForeignKey('artists.id'))
#     artist = relationship("Artist", back_populates="albums")

#starting the database
#Base.metadata.create_all(engine)

# Session = sessionmaker(bind=engine)
# session = Session()


# token = get_token()
# result = search_for_track(token, "We Found Love")



# artist_id = result['artists'][0]['id']
# tracks = get_songs_by_artist(token, artist_id)


# def add_track():
#     for item in tracks:
#         existing_track = session.query(Track).filter(Track.name == item['name']).first()
#         print(existing_track)
#         if existing_track:
#             print(f"Track '{item['name']}' already exists in the database.")
#             # return existing_track
#         else:
#             new_track = Track(name=item['name'], duration_ms=item['duration_ms'])
#             artist_name = item['artists'][0]['name']
#             print(artist_name)
#             album_name = item['album']['name']
#             print(album_name)
#             session.add(new_track)
#             existing_artist = session.query(Artist).filter(Artist.name == artist_name).first()
#             if existing_artist:
#                 new_track.artists.append(session.query(Artist).filter(Artist.name == artist_name).first())
#             existing_album = session.query(Album).filter(Album.name == album_name).first()
#             if existing_album:
#                 new_track.albums.append(session.query(Album).filter(Album.name == album_name).first())
#             session.commit()
#             session.close()
        
# add_track()




#for deleting the elements in database
# #Query all tracks
# all_tracks = session.query(Track).all()

# # Delete all tracks
# for track in all_tracks:
#     session.delete(track)

# # Commit the changes
#session.commit()
