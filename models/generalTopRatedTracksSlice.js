import { createSlice } from '@reduxjs/toolkit';

const initialState = [];

export const getGeneralTopRatedTracks = createSlice({
    name: 'topratedtracks',
    initialState,
    reducers: {
        setGeneralTopRatedTracks: (state, action) => {
            return action.payload;
        }
    }
});

export default getGeneralTopRatedTracks.reducer;

export const {
    setGeneralTopRatedTracks
} = getGeneralTopRatedTracks.actions;