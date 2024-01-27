import random
from flask import Blueprint, request, jsonify, send_file, Response, current_app
from . import db  # Import the SQLAlchemy instance
from .models import User,Track, Album, Artist, track_album_association, track_artist_association, RateTrackAssociation,likes_tracks_association, friends_association
from spotify import get_token, get_auth_header
from requests import get
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
import csv
import csv
from io import StringIO
from flask import send_file
import json
from werkzeug.utils import secure_filename
from sqlalchemy.orm import aliased
import requests
from sqlalchemy.sql import exists, and_
from sqlalchemy.exc import IntegrityError
import random as random
import os
import base64
from sqlalchemy import distinct




main = Blueprint('main', __name__)



@main.route('/signup', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('pass')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Path to the default profile picture
    default_profile_pic_path = "/Users/Peace Moongen/Desktop/profilepictures/default.jpg"

    new_user = User(name=name, email=email, profile_picture=default_profile_pic_path)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User successfully registered'}), 201

@main.route('/login', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    
    if user:
        if user.check_password(password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            return jsonify({'message': 'Invalid password'}), 401
    else:
        return jsonify({'message': 'Email not registered'}), 401

@main.route('/token/refresh', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token)




def get_tracks_with_details(user_id):
    tracks_with_details = db.session.query(
        Track.id.label('track_id'),
        Track.name.label('track_name'),
        func.group_concat(Artist.name.distinct()).label('artist_names'),
        func.group_concat(Album.name.distinct()).label('album_names'),
        func.avg(RateTrackAssociation.rating).label('average_rating'),
        RateTrackAssociation.rating.label('user_rating')  # Add user-specific rating
    ).join(
        track_artist_association, Track.id == track_artist_association.c.track_id
    ).join(
        Artist, track_artist_association.c.artist_id == Artist.id
    ).join(
        track_album_association, Track.id == track_album_association.c.track_id
    ).join(
        Album, track_album_association.c.album_id == Album.id
    ).outerjoin(
        RateTrackAssociation, (RateTrackAssociation.track_id == Track.id) & (RateTrackAssociation.user_id == user_id)
    ).group_by(
        Track.id
    ).all()

    return tracks_with_details

@main.route('/all_tracks', methods=['GET'])
@cross_origin(origin='*', headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def all_tracks():
    try:
        user_id = get_jwt_identity()
        tracks_details = get_tracks_with_details(user_id)
        
        results = [
            {
                'track_id': track.track_id,
                'track_name': track.track_name,
                'artist_names': track.artist_names,
                'album_names': track.album_names,
                'average_rating': round(track.average_rating, 2) if track.average_rating else None,
                'user_rating': track.user_rating if track.user_rating is not None else 'Not Rated'  # Include user rating
            }
            for track in tracks_details
        ]

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/search', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def search():
    query = request.args.get('query', '')  # Get search query from URL parameters
    search_keyword = f"%{query}%"
    matching_tracks = Track.query.filter(Track.name.ilike(search_keyword)).all()

    results = []
    for track in matching_tracks:
        artist_names = [artist.name for artist in track.artists]

        # Join artist names into a single string (or handle as a list, as needed)
        artists_str = ', '.join(artist_names) if artist_names else 'Unknown Artists'

        results.append({'track_id':track.id, 'track_name': track.name, 'artist_names': artists_str})
        # artist_name = track.artists[0].name

        # results.append({'track_name': track.name, 'artist_name': artist_name})

    return jsonify(results)


@main.route('/like_track', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def like_track():
    track_id = request.json.get('track_id')

    # Get the identity of the current user from the JWT token
    user_id = get_jwt_identity()

    # Retrieve the user object from the database
    user = User.query.get(user_id)
    # if not user:
    #     return jsonify({'message': 'User not found'}), 404

    track = Track.query.get(track_id)
    # if not track:
    #     return jsonify({'message': 'Track not found'}), 404

    if track in user.liked_tracks:
        return jsonify({'message': 'Track already liked'}), 409

    user.liked_tracks.append(track)
    db.session.commit()
    return jsonify({'message': f'Track {track_id} liked by you'}), 200



def get_user_liked_tracks(user_id):
    liked_tracks = db.session.query(
        Track.id.label('track_id'),
        Track.name.label('track_name'),
        func.group_concat(Artist.name.distinct()).label('artist_names'),
        func.group_concat(Album.name.distinct()).label('album_names'),
        RateTrackAssociation.rating.label('user_rating')  # Include the user's rating for the track
    ).join(
        Track.artists
    ).join(
        Track.albums
    ).join(
        likes_tracks_association, likes_tracks_association.c.track_id == Track.id
    ).outerjoin(
        RateTrackAssociation, (RateTrackAssociation.track_id == Track.id) & (RateTrackAssociation.user_id == user_id)
    ).filter(
        likes_tracks_association.c.user_id == user_id  # Make sure to only get the tracks liked by the user
    ).group_by(
        Track.id
    ).all()

    return liked_tracks


def remove_liked_track(user_id, track_id):
    # Find the specific like association for the user and track
    stmt = likes_tracks_association.delete().where(
        db.and_(
            likes_tracks_association.c.user_id == user_id,
            likes_tracks_association.c.track_id == track_id
        )
    )
    # Execute the deletion statement
    db.session.execute(stmt)
    db.session.commit()

@main.route('/remove_user_liked_tracks/<int:track_id>', methods=['DELETE'])
@cross_origin(origin='*', methods=['DELETE', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def remove_user_liked_track(track_id):
    user_id = get_jwt_identity()

    try:
        # Call the function to remove the liked track
        remove_liked_track(user_id, track_id)

        return jsonify({'message': 'Track has been removed from liked tracks'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@main.route('/user_liked_tracks', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def user_liked_tracks_endpoint():
    user_id = get_jwt_identity()

    try:
        liked_tracks = get_user_liked_tracks(user_id)

        results = [
            {
                'track_id': track.track_id,
                'track_name': track.track_name,
                'artist_names': track.artist_names,
                'album_names': track.album_names,
                'user_rating': track.user_rating if track.user_rating is not None else 'Not Rated'
            }
            for track in liked_tracks
        ]

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/rate_track', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def rate_track():
    data = request.json
    track_id = data.get('track_id')
    rating = data.get('rating')

    
    user_id = get_jwt_identity()

    rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id=track_id).first()

    if rate_association:
        # Update existing rating
        rate_association.rating = rating
    else:
        # Create a new rating
        new_rate = RateTrackAssociation(user_id=user_id, track_id=track_id, rating=rating)
        db.session.add(new_rate)

    db.session.commit()
    return jsonify({'message': 'Rating submitted successfully'}), 200

def get_user_top_rated_tracks(user_id, months=6):
    six_months_ago = datetime.utcnow() - relativedelta(months=months)

    user_top_rated_tracks = db.session.query(
        RateTrackAssociation.track_id,
        Track.name.label('track_name'),
        func.group_concat(Artist.name).label('artist_names'),
        func.group_concat(Album.name).label('album_names'),
        Track.genre.label('genre'),  # Include the genre in the query
        RateTrackAssociation.rating
    ).join(
        RateTrackAssociation.track
    ).join(
        Track.artists
    ).join(
        Track.albums
    ).filter(
        RateTrackAssociation.user_id == user_id,
        RateTrackAssociation.rated_at >= six_months_ago,
        RateTrackAssociation.rating >= 4
    ).group_by(
        RateTrackAssociation.track_id
    ).order_by(
        db.desc(RateTrackAssociation.rating)
    ).limit(10).all()

    return user_top_rated_tracks

def format_top_tracks_for_sharing(top_tracks):
    share_text = "Check out my top-rated tracks from the last 6 months:\n"
    for track in top_tracks:
        share_text += f"{track['track_name']} by {track['artist_name']} - Rating: {track['rating']}\n"
    return share_text

@main.route('/user_top_rated_tracks', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def user_top_rated_tracks():

    user_id = get_jwt_identity()
    months = request.args.get('months', default=6, type=int)

    top_tracks = get_user_top_rated_tracks(user_id, months)

    results = [
        {
            'track_id': track.track_id,
            'track_name': track.track_name,
            'artist_name': track.artist_names,
            'album_name': track.album_names,
            'rating': track.rating
        }
        for track in top_tracks
    ]
    shareable_text = format_top_tracks_for_sharing(results)
    return jsonify({'results': results, 'shareable_text': shareable_text})



def get_top_rated_tracks_statistics_page(months=6):
    six_months_ago = datetime.utcnow() - relativedelta(months=months)

    top_rated_tracks = db.session.query(
        RateTrackAssociation.track_id,
        Track.name.label('track_name'),  # Include the track name
        func.avg(RateTrackAssociation.rating).label('average_rating'),
        func.group_concat(Artist.name.distinct()).label('artist_names'),
        func.group_concat(Album.name.distinct()).label('album_names')
    ).join(
        Track, RateTrackAssociation.track_id == Track.id
    ).join(
        Track.artists
    ).join(
        Track.albums
    ).filter(
        RateTrackAssociation.rated_at >= six_months_ago
    ).group_by(
        RateTrackAssociation.track_id
    ).order_by(
        db.desc('average_rating')
    ).limit(10).all()

    return top_rated_tracks

@main.route('/top_rated_tracks', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def top_rated_tracks_endpoint():
    try:
        top_tracks = get_top_rated_tracks_statistics_page()

        results = [
            {
                'track_id': track.track_id, 
                'track_name': track.track_name,  
                'average_rating': round(track.average_rating, 2),
                'artist_names': track.artist_names,
                'album_names': track.album_names
            }
            for track in top_tracks
        ]

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_user_ratings(user_id, artist_name=None):
    query = db.session.query(
        RateTrackAssociation.track_id,
        Track.name.label('track_name'),
        Artist.name.label('artist_name'),
        RateTrackAssociation.rating
    ).join(
        RateTrackAssociation.track
    ).join(
        Track.artists
    ).filter(
        RateTrackAssociation.user_id == user_id
    )

    if artist_name:
        query = query.filter(Artist.name == artist_name)

    return query.all()

def export_ratings_to_csv(ratings):
    output = StringIO()
    writer = csv.writer(output)

    # Writing the headers
    writer.writerow(['Track ID', 'Track Name', 'Artist Name', 'Rating'])

    # Writing the data rows
    for rating in ratings:
        writer.writerow([rating.track_id, rating.track_name, rating.artist_name, rating.rating])

    output.seek(0)
    return output.getvalue()

@main.route('/export_ratings', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def export_ratings():
    user_id = get_jwt_identity()
    data = request.json
    artist_name = request.args.get('artist')

    ratings = get_user_ratings(user_id, artist_name)
    csv_data = export_ratings_to_csv(ratings)

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-disposition": "attachment; filename=ratings_export.csv"}
    )

def delete_associations(track_id):  
    db.session.execute(likes_tracks_association.delete().where(likes_tracks_association.c.track_id == track_id))
    db.session.execute(track_artist_association.delete().where(track_artist_association.c.track_id == track_id))
    db.session.execute(track_album_association.delete().where(track_album_association.c.track_id == track_id))
    RateTrackAssociation.query.filter_by(track_id=track_id).delete()

def delete_track(track_id):
    track = Track.query.get(track_id)
    if track:
        
        delete_associations(track_id)

        db.session.delete(track)
        db.session.commit()
        return True
    return False

@main.route('/delete_track/<int:track_id>', methods=['DELETE'])
@cross_origin()
@cross_origin(origin='*', methods=['DELETE', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def delete_track_endpoint(track_id):
    try:
        if delete_track(track_id):
            return jsonify({'message': 'Track deleted successfully'}), 200
        else:
            return jsonify({'message': 'Track not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


token = get_token()
def search_for_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    query_url = url + query
    responde = get(query_url, headers=headers)
    result = responde.json()["tracks"]["items"]
    if result[0]:  # If there is a result
        artist_id = result[0]['artists'][0]['id']  # Assuming you want the first artist
        genres = get_artist_genres(token, artist_id)
        result[0]['genres'] = genres  # Add the genres to the track's information

    return result[0]

def get_artist_genres(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    artist_details = response.json()
    return artist_details.get('genres', [])


@main.route('/add_track', methods=['POST'])
@cross_origin()
def add_track():
    data = request.json
    track_name = data.get('track_name')

    if not track_name:
        return jsonify({'message': 'Track name is required'}), 400

    token = get_token()
    track_data = search_for_track(token, track_name)

    if track_data and 'name' in track_data and 'duration_ms' in track_data:
        existing_track = Track.query.filter_by(name=track_data['name']).first()
        if existing_track:
            # If the track exists, return the existing info
            return {
                'message': 'Track already exists in the database',
                'track_id': existing_track.id,
                'albums': [album.name for album in existing_track.albums],
                'artists': [artist.name for artist in existing_track.artists],
                'genre': existing_track.genre  # Include genre in the response
            }, 409

        

        # Create a new Track instance with the retrieved data
        new_track = Track(
            name=track_data['name'], 
            duration_ms=track_data['duration_ms'],
            genre=','.join(track_data['genres'])  
        )


        # Find or create the associated artists
        artists = []
        for artist_data in track_data.get('artists', []):
            artist = Artist.query.filter_by(name=artist_data.get('name')).first()
            if not artist:
                artist = Artist(name=artist_data.get('name'))
                db.session.add(artist)
            artists.append(artist)
        
        # Find or create the associated album
        album_data = track_data.get('album', {})
        album = Album.query.filter_by(name=album_data.get('name')).first()
        if not album and album_data.get('name'):
            album = Album(
                name=album_data.get('name'),
                release_date=album_data.get('release_date'),
                total_tracks=album_data.get('total_tracks'),
                artist=artists[0] if artists else None
            )
            db.session.add(album)

        # Add the new track to the session
        db.session.add(new_track)

        # Associate the new track with artists and album
        for artist in artists:
            new_track.artists.append(artist)
        if album:
            new_track.albums.append(album)

        try:
            db.session.commit()
            return {
                'message': 'Track added successfully',
                'track_id': new_track.id,
                'album': album.name if album else None,
                'artists': [artist.name for artist in new_track.artists],
                'genre': new_track.genre
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    else:
        return {'message': 'Incomplete track data'}, 400



@main.route('/delete_all_tables', methods=['DELETE'])
@cross_origin()
def delete_all_tables():
    try:
        db.session.query(track_album_association).delete()
        db.session.query(track_artist_association).delete()
        db.session.query(Track).delete()
        db.session.query(User).delete()
        db.session.query(Album).delete()
        db.session.query(Artist).delete()
        db.session.commit()
        return jsonify({'message': f'All tables are now empty.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def add_track_batch(track_name):
    if not track_name:
        return {'message': 'Track name is required'}, 400

    token = get_token()
    track_data = search_for_track(token, track_name)

    if track_data and 'name' in track_data and 'duration_ms' in track_data:
        existing_track = Track.query.filter_by(name=track_data['name']).first()
        if existing_track:
            # If the track exists, return the existing info
            return {
                'message': 'Track already exists in the database',
                'track_id': existing_track.id,
                'albums': [album.name for album in existing_track.albums],
                'artists': [artist.name for artist in existing_track.artists],
                'genre': existing_track.genre  # Include genre in the response
            }, 409

        # Create a new Track instance with the retrieved data
        new_track = Track(
            name=track_data['name'], 
            duration_ms=track_data['duration_ms'],
            genre=','.join(track_data['genres'])  # Assuming the genres are returned as a list
        )


        # Find or create the associated artists
        artists = []
        for artist_data in track_data.get('artists', []):
            artist = Artist.query.filter_by(name=artist_data.get('name')).first()
            if not artist:
                artist = Artist(name=artist_data.get('name'))
                db.session.add(artist)
            artists.append(artist)
        
        # Find or create the associated album
        album_data = track_data.get('album', {})
        album = Album.query.filter_by(name=album_data.get('name')).first()
        if not album and album_data.get('name'):
            album = Album(
                name=album_data.get('name'),
                release_date=album_data.get('release_date'),
                total_tracks=album_data.get('total_tracks'),
                artist=artists[0] if artists else None
            )
            db.session.add(album)

        # Add the new track to the session
        db.session.add(new_track)

        # Associate the new track with artists and album
        for artist in artists:
            new_track.artists.append(artist)
        if album:
            new_track.albums.append(album)

        try:
            # Attempt to commit new track and associations to the database
            db.session.commit()
            return {
                'message': 'Track added successfully',
                'track_id': new_track.id,
                'album': album.name if album else None,
                'artists': [artist.name for artist in new_track.artists],
                'genre': new_track.genre
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    else:
        return {'message': 'Incomplete track data'}, 400

@main.route('/batch_upload', methods=['POST'])
@cross_origin()
def batch_input():
    # Check if a file part is present in the request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    try:

        file_content = file.read().decode('utf-8')  # Decode the file content
        file.close()  
        # Parse the content as JSON
        data = json.loads(file_content)

        track_names = data.get('track_names')
        if not track_names:
            return jsonify({'message': 'No track names provided in the file'}), 400

        results = []
        for track_name in track_names:
            result, status = add_track_batch(track_name)
            # Check the status code if you need to handle different outcomes
            results.append(result)

        return jsonify({'tracks': results}), 201  
    except json.JSONDecodeError as e:
        return jsonify({'message': 'Invalid JSON format', 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500



def add_track_batch(track_name):
    if not track_name:
        return {'message': 'Track name is required'}, 400

    token = get_token()
    track_data = search_for_track(token, track_name)

    if track_data and 'name' in track_data and 'duration_ms' in track_data:
        existing_track = Track.query.filter_by(name=track_data['name']).first()
        if existing_track:
            # If the track exists, return the existing info
            return {
                'message': 'Track already exists in the database',
                'track_id': existing_track.id,
                'albums': [album.name for album in existing_track.albums],
                'artists': [artist.name for artist in existing_track.artists],
                'genre': existing_track.genre  # Include genre in the response
            }, 409

        # Create a new Track instance with the retrieved data
        new_track = Track(
            name=track_data['name'], 
            duration_ms=track_data['duration_ms'],
            genre=','.join(track_data['genres'])  # Assuming the genres are returned as a list
        )


        # Find or create the associated artists
        artists = []
        for artist_data in track_data.get('artists', []):
            artist = Artist.query.filter_by(name=artist_data.get('name')).first()
            if not artist:
                artist = Artist(name=artist_data.get('name'))
                db.session.add(artist)
            artists.append(artist)
        
        # Find or create the associated album
        album_data = track_data.get('album', {})
        album = Album.query.filter_by(name=album_data.get('name')).first()
        if not album and album_data.get('name'):
            album = Album(
                name=album_data.get('name'),
                release_date=album_data.get('release_date'),
                total_tracks=album_data.get('total_tracks'),
                artist=artists[0] if artists else None
            )
            db.session.add(album)

        # Add the new track to the session
        db.session.add(new_track)

        # Associate the new track with artists and album
        for artist in artists:
            new_track.artists.append(artist)
        if album:
            new_track.albums.append(album)

        try:
            # Attempt to commit new track and associations to the database
            db.session.commit()
            return {
                'message': 'Track added successfully',
                'track_id': new_track.id,
                'album': album.name if album else None,
                'artists': [artist.name for artist in new_track.artists],
                'genre': new_track.genre
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    else:
        return {'message': 'Incomplete track data'}, 400



@main.route('/recommendations', methods=['GET'])
@cross_origin()
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    
    # Get user's top-rated tracks or preferences
    user_top_tracks = get_user_top_rated_tracks(user_id)

    # If there's more than one top-rated track, choose one randomly
    if len(user_top_tracks) > 1:
        chosen_track = random.choice(user_top_tracks)
        # Construct the recommendation dictionary
        recommendation = {
            'track_id': chosen_track.track_id,
            'track_name': chosen_track.track_name,
            'artist_names': chosen_track.artist_names.split(',') if chosen_track.artist_names else [],
            'album_names': chosen_track.album_names.split(',') if chosen_track.album_names else [],
            'rating': chosen_track.rating
        }
        return jsonify(recommendation), 200
    elif user_top_tracks:
        # If there's only one top-rated track, use that one
        chosen_track = user_top_tracks[0]
        recommendation = {
            'track_id': chosen_track.track_id,
            'track_name': chosen_track.track_name,
            'artist_names': chosen_track.artist_names.split(',') if chosen_track.artist_names else [],
            'album_names': chosen_track.album_names.split(',') if chosen_track.album_names else [],
            'rating': chosen_track.rating
        }
        return jsonify(recommendation), 200
    else:
        # If there are no top-rated tracks, return an appropriate message
        return jsonify({'message': 'No top rated tracks found for the user'}), 404

def get_top_rated_tracks(user_id):
    six_months_ago = datetime.utcnow() - relativedelta(months=6)

    # Aliases for association tables to be used in join conditions
    track_artist_alias = aliased(track_artist_association, name='track_artist')
    track_album_alias = aliased(track_album_association, name='track_album')

    top_tracks_query = db.session.query(
    Track.id.label('track_id'),
    func.avg(RateTrackAssociation.rating).label('average_rating'),
    func.count(RateTrackAssociation.user_id).label('rating_count'),
    func.group_concat(Artist.name.distinct()).label('artist_names'),
    func.group_concat(Album.name.distinct()).label('album_names')
).join(
    RateTrackAssociation, Track.id == RateTrackAssociation.track_id
).join(
    track_artist_alias, Track.id == track_artist_alias.c.track_id
).join(
    Artist, Artist.id == track_artist_alias.c.artist_id
).join(
    track_album_alias, Track.id == track_album_alias.c.track_id
).join(
    Album, Album.id == track_album_alias.c.album_id
).filter(
    RateTrackAssociation.rated_at >= six_months_ago
).filter(
    RateTrackAssociation.user_id == user_id
).group_by(
    Track.id
).order_by(
    func.avg(RateTrackAssociation.rating).desc()
).limit(10)

    # Execute the query and fetch all results as a list of named tuples
    top_tracks_results = top_tracks_query.all()

    # Convert the query results to a list of dictionaries
    top_tracks = []
    for track in top_tracks_results:
        track_dict = {
            'track_id': track.track_id,
            'average_rating': float(track.average_rating) if track.average_rating is not None else None,
            'rating_count': track.rating_count,
            'artist_names': track.artist_names.split(',') if track.artist_names else [],
            'album_names': track.album_names.split(',') if track.album_names else []
        }
        top_tracks.append(track_dict)

    return top_tracks

def get_top_rated_track(user_id):
    six_months_ago = datetime.utcnow() - relativedelta(months=6)

    top_track_data = db.session.query(
        RateTrackAssociation.track_id,
        func.max(RateTrackAssociation.rating).label('highest_rating')
    ).filter(
        RateTrackAssociation.user_id == user_id,
        RateTrackAssociation.rated_at >= six_months_ago
    ).group_by(
        RateTrackAssociation.track_id
    ).order_by(
        db.desc('highest_rating')
    ).first()

    if top_track_data:
        top_track = Track.query.get(top_track_data[0])
        return top_track
    return None


@main.route('/add_friend', methods=['POST'])
@cross_origin()
@jwt_required()
def add_friend():
    current_user_id = get_jwt_identity()  
    data = request.get_json()
    friend_mail = data.get('friend_email')

    if not friend_mail:
        return jsonify({'message': 'Friend email not provided'}), 400

    friend = db.session.query(User).filter_by(email=friend_mail).first()

    if not friend:
        return jsonify({'message': 'No user found with provided email'}), 404

    friend_id = friend.id  
    if current_user_id == friend_id:
        return jsonify({'message': 'Users cannot be friends with themselves'}), 400

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if friend in user.friends:
        return jsonify({'message': 'Users are already friends'}), 409

    user.friends.append(friend)
    friend.friends.append(user)

    try:
        db.session.commit()
        return jsonify({'message': 'Friend added successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message': 'This friendship already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




@main.route('/remove_friend', methods=['POST'])
@cross_origin()
@jwt_required()
def remove_friend():
    current_user_id = get_jwt_identity()  
    data = request.get_json()
    friend_mail = data.get('friend_email')

    if not friend_mail:
        return jsonify({'message': 'Friend email not provided'}), 400

    friend = db.session.query(User).filter_by(email=friend_mail).first()

    if not friend:
        return jsonify({'message': 'No user found with provided email'}), 404

    friend_id = friend.id  

    if current_user_id == friend_id:
        return jsonify({'message': 'Users cannot remove themselves'}), 400

    user = User.query.get(current_user_id)
    friend = User.query.get(friend_id)

    if not user or not friend:
        return jsonify({'message': 'User or friend not found'}), 404

    if friend not in user.friends:
        return jsonify({'message': 'Users are not friends'}), 409

    user.friends.remove(friend)
    friend.friends.remove(user)

    try:
        db.session.commit()
        return jsonify({'message': 'Friend removed successfully'}), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({'error': str(e)}), 500






@main.route('/clear_friends', methods=['POST'])
@cross_origin()
def clear_friends():
    try:
        db.session.execute(friends_association.delete())
        db.session.commit()
        return jsonify({'message': 'All friend associations have been cleared'}), 200
    except Exception as e:
        db.session.rollback()  
        return jsonify({'error': str(e)}), 500



@main.route('/recommend_friend_fav', methods=['GET'])
@cross_origin()
@jwt_required()
def recommend_friend_fav():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    top_tracks_with_ratings = []
    for friend in user.friends:
        top_track = db.session.query(RateTrackAssociation).filter_by(user_id=friend.id).order_by(RateTrackAssociation.rating.desc()).first()
        if top_track:
            top_tracks_with_ratings.append((top_track.track, top_track.rating))

    if not top_tracks_with_ratings:
        return jsonify({'message': 'No top tracks found among friends'}), 404

    recommended_track, user_rating = random.choice(top_tracks_with_ratings)

    track_info = {
        'track_id': recommended_track.id,
        'track_name': recommended_track.name,
        'user_rating': user_rating,
        'album_names': recommended_track.albums[0].name if recommended_track.albums else "Unknown Album",
        'artist_names': recommended_track.artists[0].name if recommended_track.artists else "Unknown Artist"
    }

    return jsonify({'recommended_track': track_info}), 200


@main.route('/get_friends', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def get_friends():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    friends_list = []
    for friend in user.friends:
        profile_picture_data = None
        if friend.profile_picture:
            try:
                with open(friend.profile_picture, "rb") as image_file:
                    profile_picture_data = base64.b64encode(image_file.read()).decode('utf-8')
            except IOError:
                profile_picture_data = "Error loading image"

        friend_data = {
            'id': friend.id,
            'name': friend.name,
            'email': friend.email,
            'profile_picture': profile_picture_data
        }
        friends_list.append(friend_data)

    return jsonify({'friends': friends_list}), 200

 



@main.route('/autocomplete_user_search', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def autocomplete_user_search():
    search_query = request.args.get('email', '')  

    if len(search_query) < 10: 
        return jsonify([]), 200

    potential_matches = User.query.filter(User.email.ilike(f'%{search_query}%')).limit(10).all()

    results = [{'id': user.id, 'email': user.email} for user in potential_matches]

    return jsonify(results), 200

@main.route('/recommendations_genre', methods=['GET'])
@cross_origin()
@jwt_required()
def get_recommendations_genre():
    user_id = get_jwt_identity()


    top_rated_tracks = get_user_top_rated_tracks(user_id)


    high_rated_tracks = [track for track in top_rated_tracks if track.rating >= 4]


    if not high_rated_tracks:
        return jsonify({'message': 'No high rated tracks found for the user'}), 404

    random.shuffle(high_rated_tracks)  
    for selected_track in high_rated_tracks:

        selected_genre = selected_track[4]  


        unrated_tracks_same_genre = Track.query \
            .filter(Track.genre == selected_genre) \
            .filter(~exists().where(
                and_(
                    RateTrackAssociation.track_id == Track.id,
                    RateTrackAssociation.user_id == user_id
                )
            )) \
            .all()

        if unrated_tracks_same_genre:
            recommended_track = random.choice(unrated_tracks_same_genre)
            track_info = {
                'track_id': recommended_track.id,
                'track_name': recommended_track.name,
                'artists': [artist.name for artist in recommended_track.artists],
                'genre': recommended_track.genre,
                'album': recommended_track.albums[0].name if recommended_track.albums else "Unknown Album"
            }
            return jsonify({'recommended_track': track_info}), 200

    return jsonify({'message': 'No unrated tracks found with the genres of your top-rated tracks'}), 404

@main.route('/get_my_name', methods=['GET'])
@cross_origin()
@jwt_required()  
def get_my_name():

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({'Name': user.name}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    

@main.route('/get_my_email', methods=['GET'])
@cross_origin()
@jwt_required()  
def get_my_email():

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({'email': user.email}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@main.route('/get_my_profile_picture', methods=['GET'])
@cross_origin()
@jwt_required()
def get_my_profile_picture():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.profile_picture:
        image_path = user.profile_picture
        if os.path.exists(image_path) and os.path.isfile(image_path):
            return send_file(image_path)
        else:
            return jsonify({'message': 'Profile picture file not found'}), 404
    else:
        return jsonify({'message': 'Profile picture not set'}), 404

@main.route('/recommendations_spotify', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def spotify_recommendations():
    user_id = get_jwt_identity()
    user_top_tracks = get_user_top_rated_tracks(user_id)
    chosen_track = random.choice(user_top_tracks)
    
    track_id = search_for_track(get_token(), chosen_track).get('id')
    
    recommendations = get_spotify_recommendations(get_token(), track_id)
    
    track_names = [track['name'] for track in recommendations.get('tracks', [])]

    return jsonify(track_names)

def get_spotify_recommendations(token, track_id):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    params = {
        'seed_tracks': track_id,
        'limit': 5
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.ok else {'error': 'Failed to get recommendations'}

@main.route('/upload_profile_picture', methods=['POST'])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
@jwt_required()
def upload_profile_picture():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        user.profile_picture = file_path
        db.session.commit()

        return jsonify({'message': 'Profile picture uploaded successfully'}), 200

    return jsonify({'message': 'Invalid file type'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}



@main.route('/top_rated_tracks_by_genre', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def top_rated_tracks_by_genre():
    genre = request.args.get('genre')  # Corrected line

    if not genre:
        return jsonify({'error': 'Genre is required'}), 400

    top_rated_tracks = db.session.query(
        Track.id,
        Track.name,
        Track.genre,
        func.avg(RateTrackAssociation.rating).label('average_rating')
    ).join(
        RateTrackAssociation, RateTrackAssociation.track_id == Track.id
    ).filter(
        Track.genre.like(f'%{genre}%'),
        RateTrackAssociation.rating.isnot(None)
    ).group_by(
        Track.id
    ).order_by(
        func.avg(RateTrackAssociation.rating).desc()
    ).limit(5).all()

    results = [
        {
            'track_id': track.id,
            'track_name': track.name,
            'genre': track.genre,
            'average_rating': round(track.average_rating, 2)
        } for track in top_rated_tracks
    ]

    return jsonify(results)

@main.route('/genres', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def get_unique_genres():
    # Query all distinct genres
    all_genres = db.session.query(distinct(Track.genre)).all()

    # Initialize a set to hold unique genres
    unique_genres = set()

    # Iterate over the genres, split by comma, and add to the set
    for genre_list in all_genres:
        if genre_list[0]:  # Ensure the genre string is not None
            for genre in genre_list[0].split(','):
                unique_genres.add(genre.strip())  # Strip whitespace and add

    return jsonify(sorted(unique_genres))

""" @main.route('/genres', methods=['GET'])
@cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
def get_genres():
    # Query distinct genres from the Track model
    genres_query = db.session.query(Track.genre).distinct()
    
    # Execute the query and get all results
    genres = genres_query.all()

    # Convert the results into a list of genres
    genre_list = [genre[0] for genre in genres if genre[0]]

    return jsonify(genre_list), 200 """

# from io import StringIO
# from sqlite3 import IntegrityError
# from flask import Blueprint, request, jsonify, current_app, Response
# from . import db  # Import the SQLAlchemy instance
# from .models import User,Track, Album, Artist, track_album_association, track_artist_association, RateTrackAssociation, likes_tracks_association
# from spotify import get_token, get_auth_header
# from requests import get
# from flask_cors import cross_origin
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
# from sqlalchemy import func
# import csv
# from tempfile import NamedTemporaryFile
# from flask import send_file
# import json
# from sqlalchemy.orm import aliased
# import requests
# from sqlalchemy.sql import exists, and_
# import random
# from werkzeug.utils import secure_filename
# import os




# main = Blueprint('main', __name__)



# stores = [{"name": "My Store", "items": [{"name": "my item", "price": 15.99}]}]

# @main.route('/data', methods=['GET'])
# def get_data():
#     return jsonify(stores)


# @main.route('/signup', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# def signup():
#     # data = request.json
#     # user = User(name=data['name'], email=data['email'], password=data['pass'])
#     # db.session.add(user)
#     # db.session.commit()
#     # return jsonify({'message': 'User created successfully'}), 201
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#     password = data.get('pass')
#     print(name,email,password)

#     if User.query.filter_by(email=email).first():
#         return jsonify({'message': 'Email already registered'}), 400

#     new_user = User(name=name, email=email)
#     new_user.set_password(password)

#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({'message': 'User successfully registered'}), 201

# @main.route('/login', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     user = User.query.filter_by(email=email).first()
    
#     if user:
#         if user.check_password(password):
#             access_token = create_access_token(identity=user.id)
#             refresh_token = create_refresh_token(identity=user.id)
#             return jsonify(access_token=access_token, refresh_token=refresh_token), 200
#         else:
#             return jsonify({'message': 'Invalid password'}), 401
#     else:
#         return jsonify({'message': 'Email not registered'}), 401

# @main.route('/token/refresh', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required(refresh=True)
# def refresh():
#     current_user = get_jwt_identity()
#     new_token = create_access_token(identity=current_user)
#     return jsonify(access_token=new_token)


# @main.route('/search', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# def search():
#     query = request.args.get('query', '')  # Get search query from URL parameters
#     search_keyword = f"%{query}%"
#     matching_tracks = Track.query.filter(Track.name.ilike(search_keyword)).all()

#     results = []
#     for track in matching_tracks:
#         artist_names = [artist.name for artist in track.artists]

#         # Join artist names into a single string (or handle as a list, as needed)
#         artists_str = ', '.join(artist_names) if artist_names else 'Unknown Artists'

#         results.append({'track_id':track.id, 'track_name': track.name, 'artist_names': artists_str})
#         # artist_name = track.artists[0].name

#         # results.append({'track_name': track.name, 'artist_name': artist_name})

#     return jsonify(results)


# @main.route('/like_track', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def like_track():
#     track_id = request.json.get('track_id')

#     # Get the identity of the current user from the JWT token
#     user_id = get_jwt_identity()

#     # Retrieve the user object from the database
#     user = User.query.get(user_id)
#     # if not user:
#     #     return jsonify({'message': 'User not found'}), 404

#     track = Track.query.get(track_id)
#     # if not track:
#     #     return jsonify({'message': 'Track not found'}), 404

#     if track in user.liked_tracks:
#         return jsonify({'message': 'Track already liked'}), 409

#     user.liked_tracks.append(track)
#     db.session.commit()
#     return jsonify({'message': f'Track {track_id} liked by you'}), 200


# def get_user_liked_tracks(user_id):
#     liked_tracks = db.session.query(
#         Track.id,
#         Track.name.label('track_name'),
#         func.group_concat(Artist.name.distinct()).label('artist_names'),
#         func.group_concat(Album.name.distinct()).label('album_names')
#     ).join(
#         Track.artists
#     ).join(
#         Track.albums
#     ).join(
#         Track.liked_by_users
#     ).filter(
#         User.id == user_id
#     ).group_by(
#         Track.id
#     ).all()

#     return liked_tracks

# @main.route('/user_liked_tracks', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def user_liked_tracks_endpoint():
#     user_id = get_jwt_identity()

#     try:
#         liked_tracks = get_user_liked_tracks(user_id)

#         results = [
#             {
#                 'track_id': track.id,
#                 'track_name': track.track_name,
#                 'artist_names': track.artist_names,
#                 'album_names': track.album_names
#             }
#             for track in liked_tracks
#         ]

#         return jsonify(results)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @main.route('/rate_track', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def rate_track():
#     data = request.json
#     track_id = data.get('track_id')
#     rating = data.get('rating')

#     # Assuming the identity in the JWT is the user_id
#     user_id = get_jwt_identity()

#     rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id=track_id).first()

#     if rate_association:
#         # Update existing rating
#         rate_association.rating = rating
#     else:
#         # Create a new rating
#         new_rate = RateTrackAssociation(user_id=user_id, track_id=track_id, rating=rating)
#         db.session.add(new_rate)

#     db.session.commit()
#     return jsonify({'message': 'Rating submitted successfully'}), 200

# def get_user_top_rated_tracks(user_id, months=6):
#     six_months_ago = datetime.utcnow() - relativedelta(months=months)

#     user_top_rated_tracks = db.session.query(
#         RateTrackAssociation.track_id,
#         Track.name.label('track_name'),
#         func.group_concat(Artist.name).label('artist_names'),
#         func.group_concat(Album.name).label('album_names'),
#         Track.genre.label('genre'),  # Include the genre in the query
#         RateTrackAssociation.rating
#     ).join(
#         RateTrackAssociation.track
#     ).join(
#         Track.artists
#     ).join(
#         Track.albums
#     ).filter(
#         RateTrackAssociation.user_id == user_id,
#         RateTrackAssociation.rated_at >= six_months_ago,
#         RateTrackAssociation.rating >= 4
#     ).group_by(
#         RateTrackAssociation.track_id
#     ).order_by(
#         db.desc(RateTrackAssociation.rating)
#     ).limit(10).all()

#     return user_top_rated_tracks

# @main.route('/user_top_rated_tracks', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def user_top_rated_tracks():

#     user_id = get_jwt_identity()
#     months = request.args.get('months', default=6, type=int)

#     top_tracks = get_user_top_rated_tracks(user_id, months)

#     results = [
#         {
#             'track_id': track.track_id,
#             'track_name': track.track_name,
#             'artist_name': track.artist_names,
#             'album_name': track.album_names,
#             'rating': track.rating
#         }
#         for track in top_tracks
#     ]

#     return jsonify(results)

# def get_top_rated_tracks(months=6):
#     six_months_ago = datetime.utcnow() - relativedelta(months=months)

#     top_rated_tracks = db.session.query(
#         RateTrackAssociation.track_id,
#         func.avg(RateTrackAssociation.rating).label('average_rating'),
#         func.group_concat(Artist.name.distinct()).label('artist_names'),
#         func.group_concat(Album.name.distinct()).label('album_names')
#     ).join(
#         Track, RateTrackAssociation.track_id == Track.id
#     ).join(
#         Track.artists
#     ).join(
#         Track.albums
#     ).filter(
#         RateTrackAssociation.rated_at >= six_months_ago
#     ).group_by(
#         RateTrackAssociation.track_id
#     ).order_by(
#         db.desc('average_rating')
#     ).limit(10).all()

#     return top_rated_tracks

# @main.route('/top_rated_tracks', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def top_rated_tracks_endpoint():
#     try:
#         top_tracks = get_top_rated_tracks()

#         results = [
#             {
#                 'track_id': track.track_id, 
#                 'average_rating': round(track.average_rating, 2),
#                 'artist_names': track.artist_names,
#                 'album_names': track.album_names
#             }
#             for track in top_tracks
#         ]

#         return jsonify(results)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# def get_artist_genres(token, artist_id):
#     url = f"https://api.spotify.com/v1/artists/{artist_id}"
#     headers = get_auth_header(token)
#     response = get(url, headers=headers)
#     artist_details = response.json()
#     return artist_details.get('genres', [])


# token = get_token()
# def search_for_track(token, track_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     query = f"?q={track_name}&type=track&limit=1"

#     query_url = url + query
#     responde = get(query_url, headers=headers)
#     result = responde.json()["tracks"]["items"]
#     if result[0]:  # If there is a result
#         artist_id = result[0]['artists'][0]['id']  # Assuming you want the first artist
#         genres = get_artist_genres(token, artist_id)
#         result[0]['genres'] = genres  # Add the genres to the track's information

#     return result[0]



# @main.route('/add_track', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# def add_track():
#     data = request.json
#     track_name = data.get('track_name')

#     if not track_name:
#         return jsonify({'message': 'Track name is required'}), 400

#     token = get_token()
#     track_data = search_for_track(token, track_name)

#     if track_data and 'name' in track_data and 'duration_ms' in track_data:
#         existing_track = Track.query.filter_by(name=track_data['name']).first()
#         if existing_track:
#             # If the track exists, return the existing info
#             return {
#                 'message': 'Track already exists in the database',
#                 'track_id': existing_track.id,
#                 'albums': [album.name for album in existing_track.albums],
#                 'artists': [artist.name for artist in existing_track.artists],
#                 'genre': existing_track.genre  # Include genre in the response
#             }, 409

#         # Create a new Track instance with the retrieved data
#         new_track = Track(
#             name=track_data['name'], 
#             duration_ms=track_data['duration_ms'],
#             genre=','.join(track_data['genres'])  # Assuming the genres are returned as a list
#         )


#         # Find or create the associated artists
#         artists = []
#         for artist_data in track_data.get('artists', []):
#             artist = Artist.query.filter_by(name=artist_data.get('name')).first()
#             if not artist:
#                 artist = Artist(name=artist_data.get('name'))
#                 db.session.add(artist)
#             artists.append(artist)
        
#         # Find or create the associated album
#         album_data = track_data.get('album', {})
#         album = Album.query.filter_by(name=album_data.get('name')).first()
#         if not album and album_data.get('name'):
#             album = Album(
#                 name=album_data.get('name'),
#                 release_date=album_data.get('release_date'),
#                 total_tracks=album_data.get('total_tracks'),
#                 artist=artists[0] if artists else None
#             )
#             db.session.add(album)

#         # Add the new track to the session
#         db.session.add(new_track)

#         # Associate the new track with artists and album
#         for artist in artists:
#             new_track.artists.append(artist)
#         if album:
#             new_track.albums.append(album)

#         try:
#             # Attempt to commit new track and associations to the database
#             db.session.commit()
#             return {
#                 'message': 'Track added successfully',
#                 'track_id': new_track.id,
#                 'album': album.name if album else None,
#                 'artists': [artist.name for artist in new_track.artists],
#                 'genre': new_track.genre
#             }, 201

#         except Exception as e:
#             db.session.rollback()
#             return {'message': str(e)}, 500

#     else:
#         return {'message': 'Incomplete track data'}, 400
    
    

# @main.route('/delete_all_tables', methods=['DELETE'])
# def delete_all_tables():
#     try:
#         db.session.query(track_album_association).delete()
#         db.session.query(track_artist_association).delete()
#         db.session.query(Track).delete()
#         db.session.query(User).delete()
#         db.session.query(Album).delete()
#         db.session.query(Artist).delete()
#         db.session.commit()
#         return jsonify({'message': f'All tables are now empty.'}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# @main.route('/batch_upload', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# def batch_input():
#     # Check if a file part is present in the request
#     if 'file' not in request.files:
#         return jsonify({'message': 'No file part in the request'}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400

#     try:

#         file_content = file.read().decode('utf-8')  # Decode the file content
#         file.close()  
#         # Parse the content as JSON
#         data = json.loads(file_content)

#         track_names = data.get('track_names')
#         if not track_names:
#             return jsonify({'message': 'No track names provided in the file'}), 400

#         results = []
#         for track_name in track_names:
#             result, status = add_track_batch(track_name)
#             # Check the status code if you need to handle different outcomes
#             results.append(result)

#         return jsonify({'tracks': results}), 201  
#     except json.JSONDecodeError as e:
#         return jsonify({'message': 'Invalid JSON format', 'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'message': 'An error occurred', 'error': str(e)}), 500



# def add_track_batch(track_name):
#     if not track_name:
#         return {'message': 'Track name is required'}, 400

#     token = get_token()
#     track_data = search_for_track(token, track_name)

#     if track_data and 'name' in track_data and 'duration_ms' in track_data:
#         existing_track = Track.query.filter_by(name=track_data['name']).first()
#         if existing_track:
#             # If the track exists, return the existing info
#             return {
#                 'message': 'Track already exists in the database',
#                 'track_id': existing_track.id,
#                 'albums': [album.name for album in existing_track.albums],
#                 'artists': [artist.name for artist in existing_track.artists],
#                 'genre': existing_track.genre  # Include genre in the response
#             }, 409

#         # Create a new Track instance with the retrieved data
#         new_track = Track(
#             name=track_data['name'], 
#             duration_ms=track_data['duration_ms'],
#             genre=','.join(track_data['genres'])  # Assuming the genres are returned as a list
#         )


#         # Find or create the associated artists
#         artists = []
#         for artist_data in track_data.get('artists', []):
#             artist = Artist.query.filter_by(name=artist_data.get('name')).first()
#             if not artist:
#                 artist = Artist(name=artist_data.get('name'))
#                 db.session.add(artist)
#             artists.append(artist)
        
#         # Find or create the associated album
#         album_data = track_data.get('album', {})
#         album = Album.query.filter_by(name=album_data.get('name')).first()
#         if not album and album_data.get('name'):
#             album = Album(
#                 name=album_data.get('name'),
#                 release_date=album_data.get('release_date'),
#                 total_tracks=album_data.get('total_tracks'),
#                 artist=artists[0] if artists else None
#             )
#             db.session.add(album)

#         # Add the new track to the session
#         db.session.add(new_track)

#         # Associate the new track with artists and album
#         for artist in artists:
#             new_track.artists.append(artist)
#         if album:
#             new_track.albums.append(album)

#         try:
#             # Attempt to commit new track and associations to the database
#             db.session.commit()
#             return {
#                 'message': 'Track added successfully',
#                 'track_id': new_track.id,
#                 'album': album.name if album else None,
#                 'artists': [artist.name for artist in new_track.artists],
#                 'genre': new_track.genre
#             }, 201

#         except Exception as e:
#             db.session.rollback()
#             return {'message': str(e)}, 500

#     else:
#         return {'message': 'Incomplete track data'}, 400

# @main.route('/recommendations', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def get_recommendations():
#     user_id = get_jwt_identity()
    
#     # Get user's top-rated tracks or preferences
#     user_top_tracks = get_user_top_rated_tracks(user_id)

#     # If there's more than one top-rated track, choose one randomly
#     if len(user_top_tracks) > 1:
#         chosen_track = random.choice(user_top_tracks)
#         # Construct the recommendation dictionary
#         recommendation = {
#             'track_id': chosen_track.track_id,
#             'track_name': chosen_track.track_name,
#             'artist_names': chosen_track.artist_names.split(',') if chosen_track.artist_names else [],
#             'album_names': chosen_track.album_names.split(',') if chosen_track.album_names else [],
#             'rating': chosen_track.rating
#         }
#         return jsonify(recommendation), 200
#     elif user_top_tracks:
#         # If there's only one top-rated track, use that one
#         chosen_track = user_top_tracks[0]
#         recommendation = {
#             'track_id': chosen_track.track_id,
#             'track_name': chosen_track.track_name,
#             'artist_names': chosen_track.artist_names.split(',') if chosen_track.artist_names else [],
#             'album_names': chosen_track.album_names.split(',') if chosen_track.album_names else [],
#             'rating': chosen_track.rating
#         }
#         return jsonify(recommendation), 200
#     else:
#         # If there are no top-rated tracks, return an appropriate message
#         return jsonify({'message': 'No top rated tracks found for the user'}), 404


# @main.route('/recommendations_genre', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def get_recommendations_genre():
#     user_id = get_jwt_identity()


#     top_rated_tracks = get_user_top_rated_tracks(user_id)


#     high_rated_tracks = [track for track in top_rated_tracks if track.rating >= 4]


#     if not high_rated_tracks:
#         return jsonify({'message': 'No high rated tracks found for the user'}), 404

#     random.shuffle(high_rated_tracks)  
#     for selected_track in high_rated_tracks:

#         selected_genre = selected_track[4]  


#         unrated_tracks_same_genre = Track.query \
#             .filter(Track.genre == selected_genre) \
#             .filter(~exists().where(
#                 and_(
#                     RateTrackAssociation.track_id == Track.id,
#                     RateTrackAssociation.user_id == user_id
#                 )
#             )) \
#             .all()

#         if unrated_tracks_same_genre:
#             recommended_track = random.choice(unrated_tracks_same_genre)
#             track_info = {
#                 'track_id': recommended_track.id,
#                 'track_name': recommended_track.name,
#                 'artists': [artist.name for artist in recommended_track.artists],
#                 'genre': recommended_track.genre,
#                 'album': recommended_track.albums[0].name if recommended_track.albums else "Unknown Album"
#             }
#             return jsonify({'recommended_track': track_info}), 200

#     return jsonify({'message': 'No unrated tracks found with the genres of your top-rated tracks'}), 404

# def get_top_rated_track(user_id):
#     six_months_ago = datetime.utcnow() - relativedelta(months=6)

#     # Get the top-rated track for the user within the last six months
#     top_track_data = db.session.query(
#         RateTrackAssociation.track_id,
#         func.max(RateTrackAssociation.rating).label('highest_rating')
#     ).filter(
#         RateTrackAssociation.user_id == user_id,
#         RateTrackAssociation.rated_at >= six_months_ago
#     ).group_by(
#         RateTrackAssociation.track_id
#     ).order_by(
#         db.desc('highest_rating')
#     ).first()

#     if top_track_data:
#         # Get the Track object using the track_id
#         top_track = Track.query.get(top_track_data[0])
#         return top_track
#     return None

# @main.route('/tracks_analysis', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def tracks_analysis():
#     user_id = get_jwt_identity()

#     try:
#         # Perform the query to gather track details, including the average rating and user rating
#         tracks_with_details = db.session.query(
#             Track.id.label('track_id'),
#             Track.name.label('track_name'),
#             func.group_concat(Artist.name.distinct()).label('artist_names'),
#             func.group_concat(Album.name.distinct()).label('album_names'),
#             func.avg(RateTrackAssociation.rating).label('average_rating'),
#             RateTrackAssociation.rating.label('user_rating')  # Add user-specific rating
#         ).join(
#             track_artist_association, Track.id == track_artist_association.c.track_id
#         ).join(
#             Artist, track_artist_association.c.artist_id == Artist.id
#         ).join(
#             track_album_association, Track.id == track_album_association.c.track_id
#         ).join(
#             Album, track_album_association.c.album_id == Album.id
#         ).outerjoin(
#             RateTrackAssociation, (RateTrackAssociation.track_id == Track.id) & (RateTrackAssociation.user_id == user_id)
#         ).group_by(
#             Track.id
#         ).all()

#         # Format the data for JSON response
#         tracks_data = [
#             {
#                 'track_id': track.track_id,
#                 'track_name': track.track_name,
#                 'artist_names': track.artist_names,
#                 'album_names': track.album_names,
#                 'average_rating': float(track.average_rating) if track.average_rating else None,
#                 'user_rating': track.user_rating if track.user_rating is not None else 'Not Rated'
#             }
#             for track in tracks_with_details
#         ]

#         return jsonify(tracks_data)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @main.route('/get_my_name', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()  
# def get_my_name():

#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#     if user:
#         return jsonify({'Name': user.name}), 200
#     else:
#         return jsonify({'message': 'User not found'}), 404
    

# @main.route('/get_my_email', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()  
# def get_my_email():

#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#     if user:
#         return jsonify({'email': user.email}), 200
#     else:
#         return jsonify({'message': 'User not found'}), 404

# @main.route('/recommend_friend_fav', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def recommend_friend_fav():
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)

#     if not user:
#         return jsonify({'message': 'User not found'}), 404

#     top_tracks = []
#     for friend in user.friends:
#         top_track = db.session.query(RateTrackAssociation).filter_by(user_id=friend.id).order_by(RateTrackAssociation.rating.desc()).first()
#         if top_track:
#             top_tracks.append(top_track.track)

#     if not top_tracks:
#         return jsonify({'message': 'No top tracks found among friends'}), 404

#     recommended_track = random.choice(top_tracks)

#     track_info = {
#         'track_id': recommended_track.id,
#         'track_name': recommended_track.name,
#         'user_rating': top_track.rating,
#         'album_names': recommended_track.albums[0].name if recommended_track.albums else "Unknown Album",
#         'artist_names': recommended_track.artists[0].name if recommended_track.artists else "Unknown Artist"
#     }

#     return jsonify({'recommended_track': track_info}), 200



# @main.route('/recommendations_spotify', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def spotify_recommendations():
#     user_id = get_jwt_identity()
#     user_top_tracks = get_user_top_rated_tracks(user_id)
#     chosen_track = random.choice(user_top_tracks)
    
#     track_id = search_for_track(get_token(), chosen_track).get('id')
    
#     recommendations = get_spotify_recommendations(get_token(), track_id)
    
#     track_names = [track['name'] for track in recommendations.get('tracks', [])]

#     return jsonify(track_names)

# def get_spotify_recommendations(token, track_id):
#     url = "https://api.spotify.com/v1/recommendations"
#     headers = get_auth_header(token)
#     params = {
#         'seed_tracks': track_id,
#         'limit': 5  # Adjust the limit as needed
#     }
#     response = requests.get(url, headers=headers, params=params)
#     return response.json() if response.ok else {'error': 'Failed to get recommendations'}


# @main.route('/upload_profile_picture', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def upload_profile_picture():
#     user_id = get_jwt_identity()
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({'message': 'User not found'}), 404

#     # Check if the post request has the file part
#     if 'file' not in request.files:
#         return jsonify({'message': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         # Update user's profile picture path
#         user.profile_picture = file_path
#         db.session.commit()

#         return jsonify({'message': 'Profile picture uploaded successfully'}), 200

#     return jsonify({'message': 'Invalid file type'}), 400

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# @main.route('/add_friend', methods=['POST'])
# @jwt_required()
# def add_friend():
#     current_user_id = get_jwt_identity()  
#     data = request.get_json()
#     friend_mail = data.get('friend_email')

#     if not friend_mail:
#         return jsonify({'message': 'Friend email not provided'}), 400

#     friend = db.session.query(User).filter_by(email=friend_mail).first()

#     if not friend:
#         return jsonify({'message': 'No user found with provided email'}), 404

#     friend_id = friend.id  
#     if current_user_id == friend_id:
#         return jsonify({'message': 'Users cannot be friends with themselves'}), 400

#     user = User.query.get(current_user_id)

#     if not user:
#         return jsonify({'message': 'User not found'}), 404

#     if friend in user.friends:
#         return jsonify({'message': 'Users are already friends'}), 409

#     user.friends.append(friend)
#     friend.friends.append(user)

#     try:
#         db.session.commit()
#         return jsonify({'message': 'Friend added successfully'}), 200
#     except IntegrityError as e:
#         db.session.rollback()
#         return jsonify({'message': 'This friendship already exists'}), 409
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# def remove_liked_track(user_id, track_id):
#     # Find the specific like association for the user and track
#     stmt = likes_tracks_association.delete().where(
#         db.and_(
#             likes_tracks_association.c.user_id == user_id,
#             likes_tracks_association.c.track_id == track_id
#         )
#     )
#     # Execute the deletion statement
#     db.session.execute(stmt)
#     db.session.commit()

# @main.route('/remove_user_liked_tracks/<int:track_id>', methods=['DELETE'])
# @cross_origin(origin='*', methods=['DELETE', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def remove_user_liked_track(track_id):
#     user_id = get_jwt_identity()

#     try:
#         # Call the function to remove the liked track
#         remove_liked_track(user_id, track_id)

#         return jsonify({'message': 'Track has been removed from liked tracks'}), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @main.route('/token/refresh', methods=['POST'])
# @cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required(refresh=True)
# def refresh():
#     current_user = get_jwt_identity()
#     new_token = create_access_token(identity=current_user)
#     return jsonify(access_token=new_token)



# def get_tracks_with_details(user_id):
#     tracks_with_details = db.session.query(
#         Track.id.label('track_id'),
#         Track.name.label('track_name'),
#         func.group_concat(Artist.name.distinct()).label('artist_names'),
#         func.group_concat(Album.name.distinct()).label('album_names'),
#         func.avg(RateTrackAssociation.rating).label('average_rating'),
#         RateTrackAssociation.rating.label('user_rating')  # Add user-specific rating
#     ).join(
#         track_artist_association, Track.id == track_artist_association.c.track_id
#     ).join(
#         Artist, track_artist_association.c.artist_id == Artist.id
#     ).join(
#         track_album_association, Track.id == track_album_association.c.track_id
#     ).join(
#         Album, track_album_association.c.album_id == Album.id
#     ).outerjoin(
#         RateTrackAssociation, (RateTrackAssociation.track_id == Track.id) & (RateTrackAssociation.user_id == user_id)
#     ).group_by(
#         Track.id
#     ).all()

#     return tracks_with_details

# @main.route('/all_tracks', methods=['GET'])
# @cross_origin(origin='*', headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def all_tracks():
#     try:
#         user_id = get_jwt_identity()
#         tracks_details = get_tracks_with_details(user_id)
        
#         results = [
#             {
#                 'track_id': track.track_id,
#                 'track_name': track.track_name,
#                 'artist_names': track.artist_names,
#                 'album_names': track.album_names,
#                 'average_rating': round(track.average_rating, 2) if track.average_rating else None,
#                 'user_rating': track.user_rating if track.user_rating is not None else 'Not Rated'  # Include user rating
#             }
#             for track in tracks_details
#         ]

#         return jsonify(results)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# def get_user_ratings(user_id, artist_name=None):
#     query = db.session.query(
#         RateTrackAssociation.track_id,
#         Track.name.label('track_name'),
#         Artist.name.label('artist_name'),
#         RateTrackAssociation.rating
#     ).join(
#         RateTrackAssociation.track
#     ).join(
#         Track.artists
#     ).filter(
#         RateTrackAssociation.user_id == user_id
#     )

#     if artist_name:
#         query = query.filter(Artist.name == artist_name)

#     return query.all()

# def export_ratings_to_csv(ratings):
#     output = StringIO()
#     writer = csv.writer(output)

#     # Writing the headers
#     writer.writerow(['Track ID', 'Track Name', 'Artist Name', 'Rating'])

#     # Writing the data rows
#     for rating in ratings:
#         writer.writerow([rating.track_id, rating.track_name, rating.artist_name, rating.rating])

#     output.seek(0)
#     return output.getvalue()

# @main.route('/export_ratings', methods=['GET'])
# @cross_origin(origin='*', methods=['GET', 'OPTIONS'], headers=['X-Requested-With', 'Content-Type', 'Origin'])
# @jwt_required()
# def export_ratings():
#     user_id = get_jwt_identity()
#     data = request.json
#     artist_name = data.get('artist_name')
#     # artist_name = request.args.get('artist')

#     ratings = get_user_ratings(user_id, artist_name)
#     csv_data = export_ratings_to_csv(ratings)

#     return Response(
#         csv_data,
#         mimetype='text/csv',
#         headers={"Content-disposition": "attachment; filename=ratings_export.csv"}
#     )
