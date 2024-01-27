import { changeUserRating, setAllTracks } from "../models/allTracksSlice";
import { setGeneralTopRatedTracks } from "../models/generalTopRatedTracksSlice";
import { changeTopTrackRating, setTopRatedTracks } from "../models/topRatedTracksSlice";
import { setUserLikedTracks, changeUserLikedRating, removeLikedTrack, addLikedTrack } from "../models/userLikedTracksSlice";
import { emptySplitApi } from "./mainApi";

const userToken = localStorage.getItem('access_token');

export const musicboxApi = emptySplitApi.injectEndpoints({
    endpoints: builder => ({
      getUserLikedTracks: builder.query({
        query: () => ({
            url: '/user_liked_tracks',
            headers: {
                Authorization: `Bearer ${userToken}`,
            },
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
          try {
            const { data } = await queryFulfilled;
            dispatch(setUserLikedTracks(data));
          } catch (error) {

          }
        }
      }),
      getAllTracks: builder.query({
        query: () => ({
            url: '/all_tracks',
            headers: {
                Authorization: `Bearer ${userToken}`,
            },
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
          try {
            const { data } = await queryFulfilled;
            dispatch(setAllTracks(data));
          } catch (error) {

          }
        }
      }),
      changeTrackRating: builder.mutation({
        query: (json_parameters) => ({
          url: '/rate_track',
          method: 'POST',
          headers: {
            Authorization: `Bearer ${userToken}`,
            },
          body: json_parameters
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
            try {
              dispatch(changeUserRating(args));
              dispatch(changeTopTrackRating(args));
              dispatch(changeUserLikedRating(args));
            } catch (error) {

            }
          }
      }),
      removeLike: builder.mutation({
        query: (json_parameters) => ({
          url: `/remove_user_liked_tracks/${json_parameters.track_id}`,
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${userToken}`,
            }
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
            try {
              dispatch(removeLikedTrack(args));
            } catch (error) {

            }
          }
      }),
      addLike: builder.mutation({
        query: (json_parameters) => ({
          url: '/like_track',
          method: 'POST',
          headers: {
            Authorization: `Bearer ${userToken}`,
            },
          body: json_parameters
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
            try {
              dispatch(addLikedTrack(args));
            } catch (error) {

            }
          }
      }),
      getTopRatedTracks: builder.query({
        query: () => ({
            url: '/user_top_rated_tracks',
            headers: {
                Authorization: `Bearer ${userToken}`,
            },
        }),
        transformResponse: (response) => {
            return response.results;
          },
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
          try {
            const { data } = await queryFulfilled;
            dispatch(setTopRatedTracks(data));
          } catch (error) {
            
          }
        }
      }),
      getGeneralTopRatedTracks: builder.query({
        query: () => ({
            url: '/top_rated_tracks',
            headers: {
                Authorization: `Bearer ${userToken}`,
            },
        }),
        async onQueryStarted(args, { dispatch, queryFulfilled }) {
          try {
            const { data } = await queryFulfilled;
            dispatch(setGeneralTopRatedTracks(data));
          } catch (error) {

          }
        }
      }),
      GetUserEmail: builder.query({
        query: () => ({
          url: '/get_my_email',
          headers: {
            Authorization: `Bearer ${userToken}`,
          },
        }),
        transformResponse: response => response.email,
      }),
      GetUserName: builder.query({
        query: () => ({
          url: '/get_my_name',
          headers: {
            Authorization: `Bearer ${userToken}`,
          },
        }),
        transformResponse: response => response.name,
      }),
      getFriends: builder.query({
        query: () => ({
            url: '/get_friends',
            headers: {
              Authorization: `Bearer ${userToken}`,
            },
        }),
        transformResponse: response => response.friends,
    }),
      uploadFile: builder.mutation({
        query: form_data => ({
          url: '/batch_upload',
          method: 'POST',
          body: form_data
        })
      }),
    })
  });

export const {
    useLazyGetUserLikedTracksQuery,
    useLazyGetAllTracksQuery,
    useChangeTrackRatingMutation,
    useAddLikeMutation,
    useRemoveLikeMutation,
    useLazyGetTopRatedTracksQuery,
    useLazyGetGeneralTopRatedTracksQuery,
    useLazyGetUserEmailQuery,
    useLazyGetUserNameQuery,
    useLazyGetFriendsQuery,
    useUploadFileMutation
} = musicboxApi;