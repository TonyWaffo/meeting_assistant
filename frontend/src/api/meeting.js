// Use the API URL from environment variables
const API_URL = import.meta.env.VITE_API_URL;  // This gets the value from .env or .env.production

// Get all meetings of the current user
export const getMeetings = async () => {
  try {
    const response = await fetch(`${API_URL}/meetings`, {
      method: 'GET',
      credentials: 'include',  // Include cookies in the request for session management
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to fetch meetings');
    }

    return await response.json();
  } catch (error) {
    console.error('Get meetings failed:', error.message);
    throw error;
  }
};

// Get details of a specific meeting
export const getMeetingDetails = async (meetingId) => {
  try {
    const response = await fetch(`${API_URL}/meeting/${meetingId}`, {
      method: 'GET',
      credentials: 'include',  // Include cookies in the request for session management
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to fetch meeting details');
    }

    return await response.json();
  } catch (error) {
    console.error('Get meeting details failed:', error.message);
    throw error;
  }
};

// Send a message to a meeting
export const sendMessage = async (content, meetingId = null, topic = 'question_answer') => {
  try {
    const response = await fetch(`${API_URL}/meeting/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content, meeting_id: meetingId, topic }),
      credentials: 'include',  // Include cookies in the request for session management
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to send message');
    }

    return await response.json();
  } catch (error) {
    console.error('Send message failed:', error.message);
    throw error;
  }
};

// Upload a file (e.g., a meeting transcript)
export const uploadFile = async (file, meetingId = null) => {
  try {
      const formData = new FormData();
      formData.append('file', file);

      // Just in case for some reason user can send multiple files
      if (meetingId) {
          formData.append('meetingId', meetingId);
      }

      const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          body: formData,
          credentials: 'include' // Include cookies for session management
      });

      if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Failed to upload file');
      }

      // Parse the JSON response
      const data = await response.json();

      // Return the entire 'data' object, now with the formatted 'transcript'
      return data;
  } catch (error) {
      console.error('Error uploading file:', error.message);
      throw error;
  }
};

// Send the transcript to the backend for a meeting
// export const sendTranscript = async (transcript, meetingId = null) => {
//   try {
//     const response = await fetch(`${API_URL}/send-transcript`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ transcript, meetingId }),
//       credentials: 'include', // Include cookies for session management
//     });

//     if (!response.ok) {
//       const data = await response.json();
//       throw new Error(data.error || 'Failed to send transcript');
//     }

//     // Return the response data (meeting info and messages)
//     return await response.json();
//   } catch (error) {
//     console.error('Send transcript failed:', error.message);
//     throw error;
//   }
// };

