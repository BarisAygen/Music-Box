import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeart as fullHeart } from '@fortawesome/free-solid-svg-icons';
import { faHeart as emptyHeart } from '@fortawesome/free-regular-svg-icons';
import { faStar as fullStar } from '@fortawesome/free-solid-svg-icons';
import { faStar as emptyStar } from '@fortawesome/free-regular-svg-icons';
import { useChangeTrackRatingMutation, useRemoveLikeMutation, useAddLikeMutation } from './services/musicboxApi';
import { useSelector } from 'react-redux';

export const Friends = () => {
    const [recommendedTrack, setRecommendedTrack] = useState(null);
    const [changeTrackRating] = useChangeTrackRatingMutation();
    const likedtracks = useSelector(state => state.likedTracks);
    const alltracks = useSelector(state => state.allTracks);
    const [removeliketrack] = useRemoveLikeMutation();
    const [addliketrack] = useAddLikeMutation();
    const [renderKey, setRenderKey] = useState(0); 

    useEffect(() => {
        const fetchFriendFavTrack = async () => {
            try {
                const response = await axios.get("http://localhost:5000/recommend_friend_fav", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                    },
                });

                if (response.status === 200 && response.data.recommended_track) {
                    setRecommendedTrack(response.data.recommended_track);
                }
            } catch (error) {
                console.log(error);
            }
        };
        fetchFriendFavTrack();
    }, []);

    useEffect(() => {
        setRenderKey(prevKey => prevKey + 1);
    }, [likedtracks, recommendedTrack]);
    
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

    return (
        <>
            <div className='song-list' key={renderKey}>
                <ul>
                    {recommendedTrack ? (
                        <li key={recommendedTrack.track_id} className="song-item">
                            <div>
                                <h2>{recommendedTrack.track_name}</h2>
                                <div className='name-album-container'>
                                    <p>Singer: {recommendedTrack.artist_names} - Album: {recommendedTrack.album_names}</p>
                                </div>
                            </div>
                            <div className="like-container">
                                {checkLike(recommendedTrack.track_id)}
                            </div>
                            <div className='user-rating'>
                                Your Rating:
                                {renderUserRatingStars(recommendedTrack.track_id, recommendedTrack.user_rating)}
                            </div>
                        </li>
                    ) : (
                        <p>No recommendations now</p>
                    )}
                </ul>
            </div>
        </>
    );
};