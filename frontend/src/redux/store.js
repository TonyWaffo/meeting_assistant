import { configureStore } from '@reduxjs/toolkit';
import meetingSlice from './meetingSlice';
import meetingHistorySlice from './meetingHistorySlice'

// Create the store using the combined reducers
const store = configureStore({
  reducer: {
    meeting: meetingSlice,
    meetingHistory: meetingHistorySlice,
  },
});

export default store;
