import { createSlice } from '@reduxjs/toolkit';

const initialState = [];

export const topRatedTracks = createSlice({
    name: 'topratedtracks',
    initialState,
    reducers: {
        setTopRatedTracks: (state, action) => {
            return action.payload;
        },
        changeTopTrackRating: (state, action) => {
            const index = state.findIndex(track => track.track_id === action.payload.track_id);
            state[index].rating = action.payload.rating;
        }
    }
});

export default topRatedTracks.reducer;

export const {
    setTopRatedTracks, changeTopTrackRating
} = topRatedTracks.actions;