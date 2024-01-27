import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import img1 from "./img/ThisWeeksMostListened.jpg";
import img2 from "./img/MoreOfWhatYouLike.jpg";
import img3 from "./img/PopularRadio.avif";
import img4 from "./img/TripHopClassics.jpg";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeart as fullHeart } from '@fortawesome/free-solid-svg-icons';
import { faHeart as emptyHeart } from '@fortawesome/free-regular-svg-icons';
import { useRemoveLikeMutation, useAddLikeMutation } from './services/musicboxApi';
import { useSelector } from 'react-redux';

export const Recommendations = () => {
    const [recommendedTrack, setRecommendedTrack] = useState(null);
    const [genreBasedRecommendation, setGenreBasedRecommendation] = useState(null);
    const [spotifyRecommendation, setSpotifyRecommendation] = useState(null);
    const [friendRecommendation, setFriendRecommendation] = useState(null);
    const [removeliketrack] = useRemoveLikeMutation();
    const [addliketrack] = useAddLikeMutation();
    const likedtracks = useSelector(state => state.likedTracks);
    const alltracks = useSelector(state => state.allTracks);
    
    useEffect(() => {
        const userToken = localStorage.getItem('access_token');
        const fetchRecommendations = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/recommendations', {
                    headers: { Authorization: `Bearer ${userToken}` },
                });
                if (response.data) {
                    setRecommendedTrack(response.data);
                }                
            }
            catch (error) {
                console.error('Error fetching recommendations:', error);
            }
        };

        const fetchGenreBasedRecommendations = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/recommendations_genre', {
                    headers: { Authorization: `Bearer ${userToken}` },
                });
                if (response.status === 200 && response.data.recommended_track) {
                    setGenreBasedRecommendation(response.data.recommended_track);
                }
            } 
            catch (error) {
                console.error('Error fetching genre based recommendations:', error);
            }
        };

        const fetchSpotifyRecommendation = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/recommendations_spotify', {
                    headers: { Authorization: `Bearer ${userToken}` },
                });
                if (response.data && response.data.length > 0) {
                    setSpotifyRecommendation(response.data[0]);
                } 
            } catch (error) {
                console.error('Error fetching spotify based recommendations:', error);
            }
        };        

        const fetchFriendFavTrack = async () => {
            try {
                const response = await axios.get("http://localhost:5000/recommend_friend_fav", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                    },
                });

                if (response.status === 200 && response.data.recommended_track) {
                    setFriendRecommendation(response.data.recommended_track);
                }
            } catch (error) {
                console.log(error);
            }
        };

        fetchFriendFavTrack();
        fetchRecommendations();
        fetchGenreBasedRecommendations();
        fetchSpotifyRecommendation();
    }, []);

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
            <div className="recommendations-container">
                <div className="left-column">
                    <div className="rectangle" id='left-up-rectangle'>
                        <div className='link'>
                            <h1>Check This One Out</h1>
                            <div className="song-info">
                                {recommendedTrack ? (
                                    <ul>
                                        <li key={recommendedTrack.track_id} className="song-item">
                                            <div>
                                                <h2>{recommendedTrack.track_name}</h2>
                                                <div className='name-album-container'>
                                                    <p>Singer: {recommendedTrack.artist_names} - Album: {recommendedTrack.album_names}</p>
                                                </div>
                                            </div>
                                            <div className="song-actions"> 
                                                {checkLike(recommendedTrack.track_id)}
                                            </div>
                                        </li>
                                    </ul>
                                ) : (
                                    <p>No recommendations now</p>
                                )}
                            </div>
                        </div>
                        <img src={img1} className="rectangle-image" alt='This Weeks Most Listened'/>
                    </div>
                    <div className="rectangle" id='left-down-rectangle'>
                    <div className='link'>
                        <h1>More of What You Like</h1>
                        <div className="song-info">
                            {genreBasedRecommendation ? (
                                <ul>
                                    <li key={genreBasedRecommendation.track_id} className="song-item">
                                        <div>
                                            <h2>{genreBasedRecommendation.track_name}</h2>
                                            <div className='name-album-container'>
                                                <p>Singer: {genreBasedRecommendation.artist_names} - Album: {genreBasedRecommendation.album_names}</p>
                                            </div>
                                        </div>
                                    </li>
                                    <div className="song-actions"> 
                                        {checkLike(genreBasedRecommendation.track_id)}
                                    </div>
                                </ul>
                            ) : (
                                <p>No recommendations now</p>
                            )}
                        </div>
                    </div>
                    <img src={img2} className="rectangle-image" alt='More of What You Like'/>
                </div>
                </div>
                <div className="right-column">
                    <div className="rectangle" id='right-up-rectangle'>
                        <div className='link'>
                            <h1>Popular Radio</h1>
                            <div className="song-info">
                            {spotifyRecommendation ? (
                                    <ul>
                                        <li key={spotifyRecommendation.track_id} className="song-item">
                                            <h2>Singer: {spotifyRecommendation}</h2>
                                            <div className="song-actions"> 
                                                {checkLike(spotifyRecommendation.track_id)}
                                            </div>
                                        </li>
                                    </ul>
                                ) : (
                                    <p>No Spotify recommendations now</p>
                                )}
                            </div>
                        </div>
                        <img src={img3} className="rectangle-image" alt='img'/>
                    </div>
                    <div className="rectangle" id='right-down-rectangle'>
                        <div className='link'>
                            <h1>This Week's Most Popular</h1>
                            <div className="song-info">
                                {friendRecommendation ? (
                                    <ul>
                                        <li key={friendRecommendation.track_id} className="song-item">
                                            <div>
                                                <h2>{friendRecommendation.track_name}</h2>
                                                <div className='name-album-container'>
                                                    <p>Singer: {friendRecommendation.artist_names} - Album: {friendRecommendation.album_names}</p>
                                                </div>
                                            </div>
                                            <div className="song-actions"> 
                                                {checkLike(friendRecommendation.track_id)}
                                            </div>
                                        </li>
                                    </ul>
                                ) : (
                                    <p>No recommendations now</p>
                                )}
                            </div>
                        </div>
                        <img src={img4} className="rectangle-image" alt='img'/>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Recommendations;