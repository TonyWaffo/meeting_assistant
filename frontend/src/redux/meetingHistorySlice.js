import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  id: null,
  topic:"",
};

const meetingHistorySlice = createSlice({
  name: 'meetingHistory',
  initialState,
  reducers: {
    setActiveMeeting: (state,action) => {
      const { id, topic } = action.payload;
      state.id = id;
      state.topic = topic;
    },
    clearActiveMeeting: (state) => {
      state.id = null;
      state.topic = "";
    },

  },
});

export const { 
  setActiveMeeting,
  clearActiveMeeting
} = meetingHistorySlice.actions;

export default meetingHistorySlice.reducer;
