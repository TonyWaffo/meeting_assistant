// src/auth.js

// Use the API URL from environment variables
const API_URL = import.meta.env.VITE_API_URL;  // This gets the value from .env or .env.production

// Register user
export const registerUser = async (email, password) => {
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
      credentials: 'same-origin',  // Include cookies in the request for session management
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Registration failed');
    }

    const userData = await response.json();
    // Optionally store user data in localStorage or a global state for session management
    localStorage.setItem('user', JSON.stringify(userData));
    return userData;
  } catch (error) {
    console.error('Registration failed:', error.message);
    throw error;
  }
};

// Login user
export const loginUser = async (email, password) => {
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
      credentials: 'include',  // Send cookies across origins
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Login failed');
    }

    const userData = await response.json();
    // Store user data in localStorage or context for session management
    localStorage.setItem('user', JSON.stringify(userData));
    return userData;
  } catch (error) {
    console.error('Login failed:', error.message);
    throw error;
  }
};

// Logout user
export const logoutUser = async () => {
  try {
    const response = await fetch(`${API_URL}/auth/logout`, {
      method: 'GET',
      credentials: 'include',  // Send cookies across origins
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Logout failed');
    }

    // Clear user data from localStorage when logged out
    localStorage.removeItem('user');
    return await response.json();
  } catch (error) {
    console.error('Logout failed:', error.message);
    throw error;
  }
};

// Change password
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const response = await fetch(`${API_URL}/auth/change_password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      credentials: 'include',  // Send cookies across origins
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Password change failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Password change failed:', error.message);
    throw error;
  }
};

// Helper to check if the user is logged in
export const checkSession = async () => {
  try {
    const response = await fetch(`${API_URL}/auth/check_session`, {
      method: 'GET',
      credentials: 'include',  // Send cookies across origins
    });

    if (!response.ok) {
      // If the session is invalid, log the user out by removing the data from localStorage
      localStorage.removeItem('user');
      throw new Error('Session expired or invalid. Please log in again.');
    }

    return await response.json();
  } catch (error) {
    console.error('Session check failed:', error.message);
    // Handle the session check failure, maybe redirect to login page
    throw error;
  }
};
