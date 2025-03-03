import React, { useState, useEffect } from 'react';
import { useDispatch,useSelector } from 'react-redux';
import { registerUser, loginUser, logoutUser, checkSession } from '../api/auth';
import { clearActiveMeeting } from '../redux/meetingHistorySlice';
import { closeAuthentication,openAuthentication,setUserLoggedIn,setUserLoggedOut } from '../redux/authenticationSlice';
import './Authentication.css'

import { IoCloseCircle } from "react-icons/io5";

const Authentication = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const dispatch=useDispatch();

  const isPopupOpen = useSelector((state) => state.authentication.isOpen); // access the popup visibility state
  const isLoggedIn= useSelector((state) => state.authentication.isLoggedIn)

  // Check session on mount
  useEffect(() => {
    const verifySession = async () => {
      try {
        await checkSession();
        dispatch(setUserLoggedIn())
      } catch (error) {
        dispatch(setUserLoggedOut())
      }
    };

    verifySession();
  }, []);

  // Handle form submission for registration or login
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      if (isRegistering) {
        const user = await registerUser(email, password);
        // localStorage.setItem('user', JSON.stringify(user));
        // dispatch(setUserLoggedIn());
        setIsRegistering(!isRegistering);
      } else {
        const user = await loginUser(email, password);
        localStorage.setItem('user', JSON.stringify(user));
        dispatch(setUserLoggedIn())
        closeAuthenticationPopup();
      }
      dispatch(clearActiveMeeting());
    } catch (error) {
      setErrorMessage(error.message);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await logoutUser();
      localStorage.removeItem('user');
      dispatch(setUserLoggedOut())
      closeAuthenticationPopup();
      dispatch(clearActiveMeeting());
    } catch (error) {
      setErrorMessage(error.message);
    }
  };

  // Close the authentication pupup box on the screen
  const closeAuthenticationPopup=()=>{
    dispatch(closeAuthentication());
  }

  return (
    <>
    {isPopupOpen &&
      (<div className="authentication-overlay">
        {isLoggedIn ? (
          <div>
            <IoCloseCircle className='close-icon'onClick={closeAuthenticationPopup} size={30}/>
            <p>Welcome back!</p>
            <button onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <div>
            <IoCloseCircle className='close-icon' onClick={closeAuthenticationPopup} size={30}/>
            <h2>{isRegistering ? 'Register' : 'Login'}</h2>
            <form onSubmit={handleSubmit}>
              <div>
                <label>Email:</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div>
                <label>Password:</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
              <button type="submit">{isRegistering ? 'Register' : 'Login'}</button>
            </form>
            <button onClick={() => setIsRegistering(!isRegistering)}>
              {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
            </button>
          </div>
        )}
    </div>
    )}
    </>
  );
};

export default Authentication;
