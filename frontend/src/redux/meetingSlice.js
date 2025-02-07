import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isRecording: false,
  isLoadingResponse: false, 
  transcript: '',
  file: null,
  conversationHistory: null,
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
    setFile: (state, action) => {
      state.file = action.payload; // Added reducer for file
    },
    setConversationHistory: (state, action) => {
      state.conversationHistory = action.payload; // Added reducer for conversation history
    },
    setLoadingResponse: (state, action) => {
      state.isLoadingResponse = action.payload; // Added reducer for loading state
    },
  },
});

export const { 
  startRecording, 
  stopRecording, 
  setTranscript, 
  setFile, 
  setConversationHistory, 
  setLoadingResponse 
} = meetingSlice.actions;

export default meetingSlice.reducer;
