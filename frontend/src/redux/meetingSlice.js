import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isRecording: false,
  transcript: '',
};

const meetingSlice = createSlice({
  name: 'meeting',
  initialState,
  reducers: {
    startRecording: (state) => {
      state.isRecording = true;
    },
    stopRecording: (state) => {
      state.isRecording = false;
    },
    setTranscript: (state, action) => {
      state.transcript = action.payload;
    },
  },
});

export const { startRecording, stopRecording, setTranscript } = meetingSlice.actions;
export default meetingSlice.reducer;
