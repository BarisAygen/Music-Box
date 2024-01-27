import allTracksSliceReducer from '../models/allTracksSlice';
import userLikedTracksSliceReducer from '../models/userLikedTracksSlice';
import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import { emptySplitApi } from "../services/mainApi";
import topRatedTracksSliceReducer from "../models/topRatedTracksSlice";
import generalTopRatedTracksSliceReducer from '../models/generalTopRatedTracksSlice';

export const store = configureStore({
    reducer: {
      [emptySplitApi.reducerPath]: emptySplitApi.reducer,
      allTracks: allTracksSliceReducer,
      likedTracks: userLikedTracksSliceReducer,
      topratedTracks: topRatedTracksSliceReducer,
      generalTopratedTracks: generalTopRatedTracksSliceReducer
    },
    middleware: getDefaultMiddleware => getDefaultMiddleware().concat(emptySplitApi.middleware)
});

setupListeners(store.dispatch);