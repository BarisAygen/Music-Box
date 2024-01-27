import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const emptySplitApi = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: 'http://127.0.0.1:5000' }),
  endpoints: () => ({})
});