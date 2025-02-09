import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  id: null,
  topic:"",
  transcript:""
};

const meetingHistorySlice = createSlice({
  name: 'meetingHistory',
  initialState,
  reducers: {
    setActiveMeeting: (state,action) => {
      const { id, topic,transcript="" } = action.payload;
      state.id = id;
      state.topic = topic;
      state.transcript=transcript;
    },
    clearActiveMeeting: (state) => {
      state.id = null;
      state.topic = "";
      state.transcript=""
    },

  },
});

export const { 
  setActiveMeeting,
  clearActiveMeeting
} = meetingHistorySlice.actions;

export default meetingHistorySlice.reducer;
