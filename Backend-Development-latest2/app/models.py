from app import db
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


likes_tracks_association = db.Table('likes_track_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'))
)
likes_artists_association = db.Table('likes_artists_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
)
likes_albums_association = db.Table('likes_albums_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('album_id', db.Integer, db.ForeignKey('albums.id'))
)

track_artist_association= db.Table('track_artist_association',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'))
)

track_album_association= db.Table('track_album_association',
    db.Column('album_id', db.Integer, db.ForeignKey('albums.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'))
)

friends_association = db.Table('friends_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)



class RateTrackAssociation(db.Model):
    __tablename__ = 'rates_track_association'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), primary_key=True)
    rating = db.Column(db.Integer)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    user = db.relationship('User', back_populates='rated_tracks')
    track = db.relationship('Track', back_populates='rated_by_users')



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100))
    profile_picture = db.Column(db.String(200), nullable = True)
 

    

    liked_tracks = db.relationship('Track', secondary=likes_tracks_association, back_populates="liked_by_users")
    liked_artists = db.relationship('Artist', secondary=likes_artists_association, back_populates = "liked_by_user_artist")
    liked_albums = db.relationship('Album', secondary=likes_albums_association, back_populates = "liked_by_user_album")
    rated_tracks = db.relationship('RateTrackAssociation', back_populates='user')
    friends = db.relationship(
        'User',
        secondary=friends_association,
        primaryjoin=(friends_association.c.user_id == id),
        secondaryjoin=(friends_association.c.friend_id == id),
        back_populates='friends'
    )

    friend_of = db.relationship('User', secondary=friends_association,
                                primaryjoin=(friends_association.c.friend_id == id),
                                secondaryjoin=(friends_association.c.user_id == id),
                                back_populates='friends')

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # S_id = Column(String, unique = True)
    duration_ms = db.Column(db.Integer, nullable = True)
    genre=db.Column(db.String, nullable = True)
    liked_by_users = db.relationship('User', secondary=likes_tracks_association,
                                     back_populates="liked_tracks")
    artists = db.relationship('Artist', secondary=track_artist_association,
                              back_populates="tracks")
    albums = db.relationship('Album', secondary=track_album_association,
                             back_populates="tracks")
    rated_by_users = db.relationship('RateTrackAssociation', back_populates='track')


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # s_id = Column(String, unique=True)
    # genres = Column(String)
    liked_by_user_artist = db.relationship('User', secondary=likes_artists_association, back_populates = "liked_artists")

    tracks = db.relationship('Track', secondary=track_artist_association,
                             back_populates="artists")
    
    albums = db.relationship('Album', back_populates='artist')


    # tracks = db.relationship("Track",secondary = track_artist_association, backref=db.backref('artists', lazy='dynamic'))
    # rates = db.relationship("User",secondary = rates_association, backref=db.backref('rated_artist', lazy='dynamic'))

    # tracks = relationship("Track", back_populates="artist")


class Album(db.Model):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # s_id = Column(String, unique=True)  
    release_date = db.Column(db.String)
    total_tracks = db.Column(db.Integer)


    liked_by_user_album = db.relationship('User', secondary=likes_albums_association, back_populates = "liked_albums")
    tracks = db.relationship('Track', secondary=track_album_association,
                             back_populates="albums")

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artist = db.relationship('Artist', back_populates='albums')



