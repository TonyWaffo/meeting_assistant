import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isOpen: false,
};

const authenticationSlice = createSlice({
  name: 'authentication',
  initialState,
  reducers: {
    openAuthentication: (state) => {
      state.isOpen = true;
    },
    closeAuthentication: (state) => {
      state.isOpen = false;
    },
  },
});

export const { openAuthentication, closeAuthentication } = authenticationSlice.actions;

export default authenticationSlice.reducer;
