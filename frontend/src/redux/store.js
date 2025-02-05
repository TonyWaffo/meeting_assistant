import { configureStore } from '@reduxjs/toolkit';
import meetingSlice from './meetingSlice';

// Create the store using the combined reducers
const store = configureStore({
  reducer: {
    meeting: meetingSlice,
  },
});

export default store;
