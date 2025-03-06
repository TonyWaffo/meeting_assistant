import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isOpen: false,
  isLoggedIn:false,
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
    setUserLoggedIn: (state) => {
      state.isLoggedIn = true;
    },
    setUserLoggedOut: (state) => {
      state.isLoggedIn = false;
    },
  },
});

export const { openAuthentication, closeAuthentication,setUserLoggedIn,setUserLoggedOut } = authenticationSlice.actions;

export default authenticationSlice.reducer;
