import React, { useState, useEffect, useCallback } from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeart as fullHeart } from '@fortawesome/free-solid-svg-icons';
import { faHeart as emptyHeart } from '@fortawesome/free-regular-svg-icons';
import { faStar as fullStar } from '@fortawesome/free-solid-svg-icons';
import { faStar as emptyStar } from '@fortawesome/free-regular-svg-icons';
import { useSelector } from 'react-redux';
import axios from 'axios';
import { useAddLikeMutation, useChangeTrackRatingMutation, useRemoveLikeMutation } from './services/musicboxApi';

export const Search = () => {
    const [query, setQuery] = useState('');
    const [userSearchResults, setUserSearchResults] = useState([]);
    const alltracks = useSelector(state => state.allTracks);
    const [matchingtracks, setMatchingtracks] = useState([]);
    const [addliketrack] = useAddLikeMutation();
    const [removeliketrack] = useRemoveLikeMutation();
    const likedtracks = useSelector(state => state.likedTracks);
    const [changeTrackRating] = useChangeTrackRatingMutation();
    const [friends, setFriends] = useState([]);
    const [isFriend, setIsFriend] = useState({});

    useEffect(() => {
        const fetchFriends = async () => {
            const userToken = localStorage.getItem('access_token');
            const response = await axios.get('http://localhost:5000/get_friends', {
                headers: { Authorization: `Bearer ${userToken}` },
            });
            setFriends(response.data.friends.map(friend => friend.email));
        };
        fetchFriends();
    }, []);

    useEffect(() => {
        const newIsFriend = {};
        userSearchResults.forEach(user => {
            newIsFriend[user.email] = friends.includes(user.email);
        });
        setIsFriend(newIsFriend);
    }, [userSearchResults, friends]);

    const toggleFriendship = async (email) => {
        const userToken = localStorage.getItem('access_token');
        const endpoint = isFriend[email] ? 'remove_friend' : 'add_friend';
        await axios.post(`http://localhost:5000/${endpoint}`, 
            { friend_email: email },
            {
                headers: {
                    Authorization: `Bearer ${userToken}`,
                    'Content-Type': 'application/json',
                },
            }
        );
        setIsFriend({ ...isFriend, [email]: !isFriend[email] });
    };

    const handleSearch = useCallback((query) => {
        const matches = alltracks.filter(track => 
            track.track_name.toLowerCase().includes(query.toLowerCase())
        );
        setMatchingtracks(matches);
    }, [alltracks]);

    useEffect(() => {
        fetchUserSearchResults(query);
        handleSearch(query);
    }, [query, handleSearch]);

    const renderRatingStars = (rating) => {
        const stars = [];
        for (let i = 1; i <= rating; i++) {
          stars.push(<FontAwesomeIcon icon={fullStar} key={i} />);
        }
        for (let i = rating + 1; i <= 5; i++) {
          stars.push(<FontAwesomeIcon icon={emptyStar} key={i} />);
        }
        return stars.reverse();
    };

    const renderUserRatingStars = (trackid, rating) => {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            const starIcon = i <= rating ? fullStar : emptyStar;
            stars.push(<FontAwesomeIcon icon={starIcon} key={i} onClick={() => changeTrackRating({track_id: trackid, rating: i})} />);
        }
        return stars;
    };
      
    const checkLike = useCallback((trackid) => {
        const index = alltracks.findIndex(track => track.track_id === trackid);
        const theTrack = alltracks[index];
        const isLiked = likedtracks.some(track => track.track_id === trackid);
        return isLiked ? <FontAwesomeIcon icon={fullHeart} id='heart-icon' onClick={() => removeliketrack({track_id: trackid})}/> : 
        <FontAwesomeIcon icon={emptyHeart} id='heart-icon' onClick={()=> addliketrack({track_id: trackid, 
        album_names: theTrack.album_names, artist_names: theTrack.artist_names, track_name: theTrack.track_name, user_rating: theTrack.user_rating })}/>;
    }, [alltracks, likedtracks, addliketrack, removeliketrack]);

    const fetchUserSearchResults = async (emailQuery) => {
        if (emailQuery.length >= 10) {
            const response = await axios.get(`http://127.0.0.1:5000/autocomplete_user_search?email=${emailQuery}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
            });
            setUserSearchResults(response.data);
        }
    };

    return (
        <>
            <div id="search-container">
                <input
                    type="text" name="search-bar" id="search-bar" placeholder="Search" value={query} onChange={(e) => setQuery(e.target.value)}/>
                <div className='song-list'>
                    <ul>
                        {userSearchResults.length > 0 && (
                            <ul>
                                {userSearchResults.map(user => (
                                    <li className='song-item' key={user.id}>
                                        <h2 style={{marginBottom: '1.7rem'}}>{user.email}</h2>
                                        <FontAwesomeIcon 
                                            icon={isFriend[user.email] ? fullHeart : emptyHeart} 
                                            id='heart-icon' 
                                            onClick={() => toggleFriendship(user.email)} 
                                            style={{ marginLeft: '1rem', cursor: 'pointer' }}
                                        />
                                    </li>
                                ))}
                            </ul>
                        )}
                        {matchingtracks.length > 0 ? (
                            matchingtracks.map((track, index) => (
                                <li className="song-item">
                                    <div>
                                        <h2>{track.track_name}</h2>
                                        <div className='name-album-container'>
                                            <p>Singer: {track.artist_names} - Album: {track.album_names}</p>
                                        </div>
                                    </div>
                                    <div className="star-rating">
                                        {renderRatingStars(track.average_rating)}
                                    </div>
                                    <div className="like-container">
                                        {checkLike(track.track_id)}
                                    </div>
                                    <div className='user-rating'>
                                        Your Rating:
                                        {renderUserRatingStars(track.track_id, track.user_rating)}
                                    </div>
                                </li>               
                            ))
                        ) : (
                            <p>Please search for a song.</p>
                        )}
                    </ul>
                </div>
            </div>
        </>
    );
};