import { createSlice } from '@reduxjs/toolkit';

const initialState = [];

export const allTracksSlice = createSlice({
    name: 'userlikedtracks',
    initialState,
    reducers: {
        setAllTracks: (_, action) => {
            return action.payload;
        },
        changeUserRating: (state, action) => {
            const index = state.findIndex(track => track.track_id === action.payload.track_id);
            console.log(action.payload);
            if (index !== -1) {
              state[index].user_rating = action.payload.rating;
            }
        }
    }
});

export default allTracksSlice.reducer;

export const {
    setAllTracks, changeUserRating
} = allTracksSlice.actions;
