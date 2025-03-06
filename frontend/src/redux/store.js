import { configureStore } from '@reduxjs/toolkit';
import meetingSlice from './meetingSlice';
import meetingHistorySlice from './meetingHistorySlice';
import authenticationReducer from './authenticationSlice'

// Create the store using the combined reducers
const store = configureStore({
  reducer: {
    meeting: meetingSlice,
    meetingHistory: meetingHistorySlice,
    authentication: authenticationReducer,
  },
});

export default store;
