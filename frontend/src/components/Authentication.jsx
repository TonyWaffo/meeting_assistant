import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { registerUser, loginUser, logoutUser, checkSession } from '../api/auth';
import { clearActiveMeeting } from '../redux/meetingHistorySlice';

const Authentication = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const dispatch=useDispatch();

  // Check session on mount
  useEffect(() => {
    const verifySession = async () => {
      try {
        await checkSession();
        setIsLoggedIn(true);
      } catch (error) {
        setIsLoggedIn(false);
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
        localStorage.setItem('user', JSON.stringify(user));
        setIsLoggedIn(true);
      } else {
        const user = await loginUser(email, password);
        localStorage.setItem('user', JSON.stringify(user));
        setIsLoggedIn(true);
      }
    } catch (error) {
      setErrorMessage(error.message);
    }

    dispatch(clearActiveMeeting());
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await logoutUser();
      localStorage.removeItem('user');
      setIsLoggedIn(false);
    } catch (error) {
      setErrorMessage(error.message);
    }

    dispatch(clearActiveMeeting());
  };

  return (
    <div>
      {isLoggedIn ? (
        <div>
          <p>Welcome back!</p>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <div>
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
  );
};

export default Authentication;
