import pytest
from app import create_app, db
from app.models import User, Track, RateTrackAssociation, Artist, Album
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime
from dateutil.relativedelta import relativedelta

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['SECRET_KEY'] = 'aaa'  # You can set a simple key for testing
    app.config['JWT_SECRET_KEY'] = 'Akdsr45vfdfgddf3467' 
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# SIGNUP
# def test_duplicate_signup(client):
#     # Given: Signup data
#     signup_data = {
#         "name": "Test User",
#         "email": "test@example.com",
#         "pass": "testpassword"
#     }

#     # When: First signup attempt
#     response = client.post('/signup', json=signup_data)

#     # Then: Expect successful signup
#     assert response.status_code == 201, "First signup attempt should be successful"

#     # When: Second signup attempt with the same email
#     response = client.post('/signup', json=signup_data)

#     # Then: Expect failure due to duplicate email
#     assert response.status_code == 400, "Duplicate signup attempt should fail"
#     assert "Email already registered" in response.json['message']

#LOGIN
# def test_login(client, app):
#     # First, create a user to log in
#     with app.app_context():
#         user = User(name="Test User", email="test@example.com")
#         user.set_password("password")
#         db.session.add(user)
#         db.session.commit()

#     # Given: Login data
#     login_data = {
#         "email": "test@example.com",
#         "password": "password"
#     }

#     # When: Attempting to log in
#     response = client.post('/login', json=login_data)

#     # Then: Expect login to be successful
#     assert response.status_code == 200
#     assert 'access_token' in response.json
#     assert 'refresh_token' in response.json

# def test_login_with_wrong_password(client,app):
#     # Assuming a user already exists from the previous test
#     # Given: Login data with wrong password
#     with app.app_context():
#         user = User(name="Test User", email="test@example.com")
#         user.set_password("password")
#         db.session.add(user)
#         db.session.commit()

#     login_data = {
#         "email": "test@example.com",
#         "password": "wrongpassword"
#     }

#     # When: Attempting to log in with wrong password
#     response = client.post('/login', json=login_data)

#     # Then: Expect login to fail
#     assert response.status_code == 401
#     assert "Invalid password" in response.json['message']

# def test_login_with_unregistered_email(client,app):

#     with app.app_context():
#         user = User(name="Test User", email="test@example.com")
#         user.set_password("password")
#         db.session.add(user)
#         db.session.commit()
#     # Given: Login data with an unregistered email
#     login_data = {
#         "email": "unregistered@example.com",
#         "password": "somepassword"
#     }

#     # When: Attempting to log in with unregistered email
#     response = client.post('/login', json=login_data)

#     # Then: Expect login to fail
#     assert response.status_code == 401
#     assert "Email not registered" in response.json['message']

#ALL_TRACKS
# def create_test_user(email='test@example.com', password='testpassword'):
#     user = User(email=email, name='Test User')
#     user.password_hash = generate_password_hash(password)
#     db.session.add(user)
#     db.session.commit()
#     return user

# def create_test_track(id, name='Test Track'):
#     track = Track(id=id, name=name, duration_ms=12345, genre="Test Genre")
#     db.session.add(track)
#     db.session.commit()
#     return track

# def test_all_tracks(client, app):
#     with app.app_context():
#         # Create and set up data within the same app context
#         test_user = create_test_user()
#         access_token = create_access_token(identity=test_user.id)

#         test_artist = Artist(name='Test Artist')
#         db.session.add(test_artist)
#         db.session.commit()

#         test_album = Album(name='Test Album', release_date='2022-01-01', total_tracks=10, artist_id=test_artist.id)
#         db.session.add(test_album)
#         db.session.commit()

#         test_track = Track(name='Test Track', duration_ms=12345, genre="Test Genre")
#         test_track.artists.append(test_artist)
#         test_track.albums.append(test_album)
#         db.session.add(test_track)
#         db.session.commit()

#         rating = RateTrackAssociation(user_id=test_user.id, track_id=test_track.id, rating=5)
#         db.session.add(rating)
#         db.session.commit()

#         # Accessing lazy-loaded attributes here should be safe
#         track_id = test_track.id
#         track_name = test_track.name

#     # Test the /all_tracks endpoint outside of the app context
#     response = client.get('/all_tracks', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200
#     data = response.json
#     assert len(data) > 0
#     assert data[0]['track_id'] == track_id
#     assert data[0]['track_name'] == track_name
#     # Additional validations

#SEARCH 
# def setup_data():
#     """Create sample data for testing."""
#     artist1 = Artist(name="Artist One")
#     artist2 = Artist(name="Artist Two")
#     db.session.add(artist1)
#     db.session.add(artist2)
#     db.session.commit()

#     track1 = Track(name="Track One", artists=[artist1])
#     track2 = Track(name="Track Two", artists=[artist2])
#     db.session.add(track1)
#     db.session.add(track2)
#     db.session.commit()

# def test_search_tracks(client):
#     # Setup test data
#     with client.application.app_context():
#         setup_data()

#     # Perform a search query
#     response = client.get('/search?query=Track')
#     assert response.status_code == 200
#     data = response.get_json()

#     # Assert the search result content
#     assert len(data) == 2  # Assuming there are 2 tracks in the database
#     assert data[0]['track_name'] == "Track One"
#     assert data[0]['artist_names'] == "Artist One"
#     assert data[1]['track_name'] == "Track Two"
#     assert data[1]['artist_names'] == "Artist Two"

#LIKE_TRACK
# @pytest.fixture
# def auth_header(app):
#     with app.app_context():
#         # Generate a JWT token for a dummy user ID
#         access_token = create_access_token(identity=1)  # Use a placeholder user ID
#     return {'Authorization': f'Bearer {access_token}'}

# def test_like_track(client, app):
#     with app.app_context():
#         # Setup test data within context
#         user = User(email='test@example.com', name='Test User')
#         user.set_password('password')
#         db.session.add(user)
        
#         track = Track(name='Test Track')
#         db.session.add(track)
        
#         db.session.flush()  # Assign IDs without committing

#         # Generate a real JWT token for the created user
#         access_token = create_access_token(identity=user.id)
#         auth_header = {'Authorization': f'Bearer {access_token}'}

#         response = client.post('/like_track', json={'track_id': track.id}, headers=auth_header)
#         assert response.status_code == 200

#         db.session.refresh(user)  # Refresh user to update liked_tracks
        
#         # Now verify the track is in the user's liked_tracks
#         liked_tracks_ids = [t.id for t in user.liked_tracks]
#         assert track.id in liked_tracks_ids

#         # Attempt to like the same track again
#         response = client.post('/like_track', json={'track_id': track.id}, headers=auth_header)
#         assert response.status_code == 409

#REMOVE_USER_LIKED_TRACK
# @pytest.fixture
# def new_user_and_track(app):
#     with app.app_context():
#         user = User(email='testuser@example.com', name='Test User')
#         user.set_password('testpassword')
#         db.session.add(user)

#         track = Track(name='Test Track')
#         db.session.add(track)

#         db.session.commit()
#         return user.id, track.id

# @pytest.fixture
# def auth_header(app, new_user_and_track):
#     user_id, _ = new_user_and_track
#     with app.app_context():
#         access_token = create_access_token(identity=user_id)
#     return {'Authorization': f'Bearer {access_token}'}

# def test_remove_user_liked_track(client, app, new_user_and_track, auth_header):
#     user_id, track_id = new_user_and_track

#     # First, the user likes the track
#     with app.app_context():
#         user = User.query.get(user_id)
#         track = Track.query.get(track_id)
#         user.liked_tracks.append(track)
#         db.session.commit()

#     # Now, remove the liked track
#     response = client.delete(f'/remove_user_liked_tracks/{track_id}', headers=auth_header)
#     assert response.status_code == 200
#     assert b'Track has been removed from liked tracks' in response.data

#     # Verify the track is no longer in the user's liked tracks
#     with app.app_context():
#         user = User.query.get(user_id)
#         assert track not in user.liked_tracks

#     # Attempt to remove the same track again, should still succeed but the track is already removed
#     response = client.delete(f'/remove_user_liked_tracks/{track_id}', headers=auth_header)
#     assert response.status_code == 200 or response.status_code == 404

#GET_MY_EMAIL AND GET_MY_NAME
# @pytest.fixture
# def auth_header(app):
#     with app.app_context():
#         user = User(email='test@example.com', name='Test User')
#         user.set_password('testpassword')
#         db.session.add(user)
#         db.session.commit()

#         access_token = create_access_token(identity=user.id)
#         return {'Authorization': f'Bearer {access_token}'}


# def test_get_my_name(client, auth_header):
#     response = client.get('/get_my_name', headers=auth_header)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['Name'] == 'Test User'

# def test_get_my_email(client, auth_header):
#     response = client.get('/get_my_email', headers=auth_header)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['email'] == 'test@example.com'


#USER_LIKED_TRACKS_ENDPOINT
# @pytest.fixture
# def setup_data(app):
#     with app.app_context():
#         user = User(email='test@example.com', name='Test User')
#         user.set_password('testpassword')
#         db.session.add(user)

#         # Create an artist instance
#         artist = Artist(name='Test Artist')
#         db.session.add(artist)
#         db.session.commit()  # Commit to ensure artist gets an ID

#         # Now when creating an album, associate it with the artist
#         album = Album(name='Test Album', release_date='2022-01-01', total_tracks=10, artist_id=artist.id)
#         db.session.add(album)
#         db.session.commit()

#         track1 = Track(name='Test Track 1')
#         track2 = Track(name='Test Track 2')
        
#         # Assuming the relationships are set up to automatically handle association table entries
#         track1.artists.append(artist)
#         track1.albums.append(album)
#         track2.artists.append(artist)
#         track2.albums.append(album)

#         db.session.add(track1)
#         db.session.add(track2)
        
#         # Associate tracks as liked by the user
#         user.liked_tracks.append(track1)
#         user.liked_tracks.append(track2)
        
#         # Optionally, add user ratings for tracks
#         rating1 = RateTrackAssociation(user_id=user.id, track_id=track1.id, rating=5)
#         db.session.add(rating1)
        
#         db.session.commit()

#         return user.id  # Returning user ID for generating auth token


# @pytest.fixture
# def auth_header(app, setup_data):
#     user_id = setup_data
#     with app.app_context():
#         access_token = create_access_token(identity=user_id)
#     return {'Authorization': f'Bearer {access_token}'}

# def test_user_liked_tracks_endpoint(client, auth_header):
#     # Make a GET request to the endpoint
#     response = client.get('/user_liked_tracks', headers=auth_header)
#     assert response.status_code == 200
#     data = response.get_json()

#     # Assert on the returned data
#     assert len(data) == 2  # Assuming the user liked two tracks
#     assert data[0]['track_name'] == 'Test Track 1'
#     assert data[0]['user_rating'] == 5  # Check if the rating is correctly associated
#     assert data[1]['track_name'] == 'Test Track 2'
#     assert data[1]['user_rating'] == 'Not Rated' 


#RATE_TRACK
# @pytest.fixture
# def setup_data(app):
#     with app.app_context():
#         user = User(email='test@example.com', name='Test User')
#         user.set_password('testpassword')
#         db.session.add(user)

#         track = Track(name='Test Track')
#         db.session.add(track)

#         db.session.commit()

#         return user.id, track.id

# @pytest.fixture
# def auth_header(app, setup_data):
#     user_id, _ = setup_data
#     with app.app_context():
#         access_token = create_access_token(identity=user_id)
#     return {'Authorization': f'Bearer {access_token}'}


# def test_rate_track(client, app, setup_data, auth_header):
#     user_id, track_id = setup_data

#     # Rate the track
#     response = client.post('/rate_track', json={'track_id': track_id, 'rating': 5}, headers=auth_header)
#     assert response.status_code == 200
#     assert b'Rating submitted successfully' in response.data

#     # Verify the rating in the database
#     with app.app_context():
#         rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id=track_id).first()
#         assert rate_association is not None
#         assert rate_association.rating == 5

#     # Update the rating for the same track
#     response = client.post('/rate_track', json={'track_id': track_id, 'rating': 3}, headers=auth_header)
#     assert response.status_code == 200
#     assert b'Rating submitted successfully' in response.data

#     # Verify the updated rating in the database
#     with app.app_context():
#         rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id=track_id).first()
#         assert rate_association.rating == 3



#USER_TOP_RATED_TRACKS
# @pytest.fixture
# def setup_user_and_tracks(app):
#     with app.app_context():
#         user = User(email='user@example.com', name='Test User')
#         user.set_password('password')
#         db.session.add(user)

#         artist = Artist(name="Test Artist")
#         db.session.add(artist)

#         album = Album(name="Test Album", artist=artist)
#         db.session.add(album)

#         tracks = [
#             Track(name=f'Test Track {i}', artists=[artist], albums=[album]) for i in range(1, 6)
#         ]
#         for track in tracks:
#             db.session.add(track)
        
#         db.session.commit()

#         # Rate tracks
#         for track in tracks[:3]:  # Rate first three tracks
#             rating = RateTrackAssociation(user_id=user.id, track_id=track.id, rating=5, rated_at=datetime.utcnow() - relativedelta(weeks=2))
#             db.session.add(rating)
        
#         db.session.commit()

#         return user.id, [track.id for track in tracks]

# @pytest.fixture
# def auth_header(app, setup_user_and_tracks):
#     user_id, _ = setup_user_and_tracks
#     with app.app_context():
#         access_token = create_access_token(identity=user_id)
#     return {'Authorization': f'Bearer {access_token}'}


# def test_user_top_rated_tracks(client, auth_header, setup_user_and_tracks):
#     _, track_ids = setup_user_and_tracks

#     response = client.get('/user_top_rated_tracks?months=3', headers=auth_header)  # Adjust the months as needed
#     assert response.status_code == 200
#     data = response.get_json()
#     results = data['results']

#     assert len(results) == 3  # Expecting three top-rated tracks
#     for result in results:
#         assert result['track_id'] in track_ids
#         assert result['rating'] == 5  # Expecting a rating of 5 for top-rated tracks

#     shareable_text = data['shareable_text']
#     assert 'Test Track' in shareable_text  # Simple check to ensure shareable text includes track names





































































# def test_search(client):
#     # assuming there are some tracks in the database
#     test_track = Track(name='TestTrack', duration_ms=300000, genre='TestGenre')
#     db.session.add(test_track)

#     db.session.commit()

#     response = client.get('/search', query_string={'query': 'TestTrack'})
#     assert response.status_code == 200
#     assert len(response.get_json()) > 0

# def test_user_liked_tracks(client):
#     access_token = login(client) 

#     response = client.post('/like_track', json={'track_id': "2"}, headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     user_id = User.query.filter_by(email='emir.bjk.1999@gmail.com').first().id

#     response = client.get('/user_liked_tracks', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     data = response.get_json()
#     print("data: ", data, "\n")
#     track_id_to_check = "1"  # modify this based on your test case
#     track_found = any(str(track['track_id']).strip().lower() == track_id_to_check.strip().lower() for track in data)
#     assert track_found, f"Track with track_id {track_id_to_check} not found in the response"

# def test_remove_user_liked_track(client):
#     access_token = login(client)

#     response = client.delete('/remove_user_liked_tracks/2', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     track_id_to_check = "2"
#     response = client.get('/user_liked_tracks', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200
#     data = response.get_json()
#     track_found = any(str(track['track_id']).strip().lower() == track_id_to_check.strip().lower() for track in data)
#     assert not track_found, f"Track with track_id {track_id_to_check} still found in the response after removal"

# def test_rate_track(client):
#     access_token = login(client)

#     response = client.post('/rate_track', json={'track_id': "2", 'rating': 5}, headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     user_id = User.query.filter_by(email='emir.bjk.1999@gmail.com').first().id
#     rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id="2").first()
#     assert rate_association is not None
#     assert rate_association.rating == 5 

#     # updating the rating for the track
#     response = client.post('/rate_track', json={'track_id': "2", 'rating': 3}, headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     rate_association = RateTrackAssociation.query.filter_by(user_id=user_id, track_id="2").first()
#     assert rate_association is not None
#     assert rate_association.rating == 3

# def test_user_top_rated_tracks(client):
#     access_token = login(client)

#     response = client.get('/user_top_rated_tracks', headers={'Authorization': f'Bearer {access_token}', 'months': 6})
#     assert response.status_code == 200

#     data = response.get_json()
#     assert 'results' in data
#     assert 'shareable_text' in data

#     results = data['results']
#     assert isinstance(results, list)
#     assert all(isinstance(track, dict) for track in results)
#     assert all(key in track for track in results for key in ['track_id', 'track_name', 'artist_name', 'album_name', 'rating'])

#     shareable_text = data['shareable_text']
#     assert isinstance(shareable_text, str) 

# def test_top_rated_tracks_endpoint(client):
#     access_token = login(client)

#     response = client.get('/top_rated_tracks', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     data = response.get_json()
#     assert isinstance(data, list)
#     assert all(isinstance(track, dict) for track in data)
#     assert all(key in track for track in data for key in ['track_id', 'track_name', 'average_rating', 'artist_names', 'album_names'])

# def test_delete_track_endpoint(client):
#     access_token = login(client)

#     response = client.delete('/delete_track/1', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code in [200, 404]  # depends on whether the track is found or not

#     # example:
#     if response.status_code == 200:
#         assert response.get_json()['message'] == 'Track deleted successfully'
#     elif response.status_code == 404:
#         assert response.get_json()['message'] == 'Track not found' 

# def test_get_my_name(client):
#     access_token = login(client)
#     response = client.get('/get_my_name', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code in [200, 404]  # depends on whether the user is found or not

#     # example:
#     if response.status_code == 200:
#         assert 'Name' in response.get_json()
#     elif response.status_code == 404:
#         assert response.get_json()['message'] == 'User not found'


# def test_get_my_email(client):
#     access_token = login(client)
#     response = client.get('/get_my_email', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code in [200, 404]  # depends on whether the user is found or not

#     # example:
#     if response.status_code == 200:
#         assert 'email' in response.get_json()
#     elif response.status_code == 404:
#         assert response.get_json()['message'] == 'User not found'

# def test_autocomplete_user_search(client):
#     access_token = login(client)
#     response = client.get('/autocomplete_user_search', headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}, query_string={'email': 'test'})
    
#     assert response.status_code == 200
#     assert response.get_json() == []

#     response = client.get('/autocomplete_user_search', headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}, query_string={'email': 'example'})
#     assert response.status_code == 200

#     # example:
#     data = response.get_json()
#     assert isinstance(data, list)
#     assert all(isinstance(match, dict) and 'id' in match and 'email' in match for match in data)

# def test_get_friends(client):
#     access_token = login(client)
#     response = client.get('/get_friends', headers={'Authorization': f'Bearer {access_token}'})
#     assert response.status_code == 200

#     # example:
#     data = response.get_json()
#     assert isinstance(data, dict)
#     assert 'friends' in data and isinstance(data['friends'], list)

#     # example:
#     for friend in data['friends']:
#         assert 'id' in friend and 'name' in friend and 'email' in friend