import { useState, useEffect } from 'react';
import { useSelector, useDispatch} from 'react-redux';

import { uploadFile } from "../api/meeting"; // Import your sendTranscript function
import { setActiveMeeting } from '../redux/meetingHistorySlice';

const useAudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  const activeMeeting = useSelector((state) => state.meetingHistory);

  useEffect(() => {
    // Check if the MediaRecorder API is available
    if (navigator.mediaDevices && MediaRecorder) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
          const recorder = new MediaRecorder(stream);
          recorder.ondataavailable = (event) => {
            const blob = event.data;
            setAudioBlob(blob);
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);  // You can use this URL to play the audio or download it
          };

          recorder.onstop = async () => {};

          setMediaRecorder(recorder);
        })
        .catch((err) => {
          console.error('Error accessing microphone', err);
        });
    } else {
      console.error('MediaRecorder not supported in this browser.');
    }
  }, []);

  useEffect(() => {
    // Whenever audioBlob or audioUrl changes, log the updated values
    console.log("Updated Blob:", audioBlob);
    console.log("Updated URL:", audioUrl);
  }, [audioBlob, audioUrl]); // This hook will trigger whenever these values change

  const startRecording = () => {
    if (mediaRecorder) {
      setAudioBlob(null); // Clear any existing audio
      mediaRecorder.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const clearAudioBlobAndUrl = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    console.log("audio recording cleared");
  };

  return {
    recording,
    startRecording,
    stopRecording,
    audioBlob,
    audioUrl,
    clearAudioBlobAndUrl,
  };
};

export default useAudioRecorder;
