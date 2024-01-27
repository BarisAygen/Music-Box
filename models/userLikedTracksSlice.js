import { createSlice } from '@reduxjs/toolkit';

const initialState = [];

export const userLikedTracksSlice = createSlice({
    name: 'userlikedtracks',
    initialState,
    reducers: {
        setUserLikedTracks: (state, action) => {
            return action.payload;
        },
        changeUserLikedRating: (state, action) => {
            const index = state.findIndex(track => track.track_id === action.payload.track_id);
            console.log(action.payload);
            if (index !== -1) {
              state[index].user_rating = action.payload.rating;
            }
          },
          removeLikedTrack: (state, action) => {
            return state.filter(track => track.track_id !== action.payload.track_id);
          },
        addLikedTrack: (state, action) => {
            state.push(action.payload);
        }
                   
    }
});

export default userLikedTracksSlice.reducer;

export const {
    setUserLikedTracks, changeUserLikedRating, removeLikedTrack, addLikedTrack
} = userLikedTracksSlice.actions;