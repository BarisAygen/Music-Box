import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { useSelector } from 'react-redux';
import { useChangeTrackRatingMutation, useRemoveLikeMutation } from './services/musicboxApi';
import { faStar as fullStar } from '@fortawesome/free-solid-svg-icons';
import { faStar as emptyStar } from '@fortawesome/free-regular-svg-icons';

export const Songs = () => {
    const [changeTrackRating] = useChangeTrackRatingMutation();
    const [removelikemutation] = useRemoveLikeMutation();
    const likedTracks = useSelector(state => state.likedTracks);
    const [renderKey, setRenderKey] = useState(0);
    const [likedTracksState, setLikedTracksState] = useState(likedTracks);

    useEffect(() => {
    setLikedTracksState(likedTracks);
    }, [likedTracks]);

    useEffect(() => {
        setRenderKey(prevKey => prevKey + 1);
    }, [likedTracks]);

    const handleRatingChange = async (trackid, newRating) => {
        try {
          await changeTrackRating({ track_id: trackid, rating: newRating }).unwrap();
          const updatedTracks = likedTracksState.map(track =>
            track.track_id === trackid ? { ...track, user_rating: newRating } : track
          );
          setLikedTracksState(updatedTracks);
        } catch (error) {
          console.error('Error updating rating:', error);
        }
      };      

    const renderUserRatingStars = (trackid, rating) => {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            const starIcon = i <= rating ? fullStar : emptyStar;
            stars.push(<FontAwesomeIcon icon={starIcon} key={i} onClick={() => handleRatingChange(trackid, i)} />);
        }
        return stars;
    };
      
    const handleDelete = (track_id) => {
        removelikemutation({track_id: track_id});
        const updatedTracks = likedTracksState.filter(track => track.track_id !== track_id);
        setLikedTracksState(updatedTracks);
      }      
    
    return (
        <>
            <div className='song-list' key={renderKey}>
                <ul>
                    {likedTracks && likedTracks.map((song) => (
                        <li key={song.id} className="song-item">
                            <div>
                                <h2>{song.track_name}</h2>
                                <div className='name-album-container'>
                                    <p>Singer: {song.artist_names} - Album: {song.album_names}</p>
                                </div>
                            </div>
                            <div className='user-rating'>
                                Your Rating:
                                {renderUserRatingStars(song.track_id, song.user_rating)}
                            </div>
                            <span role="img" aria-label="Delete" onClick={() => handleDelete(song.track_id)}>
                                <FontAwesomeIcon icon={faTrash} id="delete-icon"/>
                            </span>
                        </li>
                    ))}
                </ul>
            </div>
        </>
    );
};