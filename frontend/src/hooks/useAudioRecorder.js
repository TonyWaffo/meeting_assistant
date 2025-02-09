import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';

const useAudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [transcribedText, setTranscribedText] = useState("");
  const [recognitionInstance, setRecognitionInstance] = useState(null);

  const activeMeeting=useSelector((state)=>state.meetingHistory)

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const instance = new SpeechRecognition();
      instance.continuous = true;
      instance.interimResults = true;
      instance.lang = 'fr-FR';

      instance.onresult = (event) => {
        let finalTranscript = '';
        if (event.results[event.resultIndex].isFinal) {
          finalTranscript = event.results[event.resultIndex][0].transcript + " ";
          setTranscribedText((prevText) => prevText + finalTranscript);
        }
      };

      instance.onerror = (event) => {
        console.error("Speech Recognition Error", event);
        setTranscribedText("Error occurred during speech recognition");
      };

      setRecognitionInstance(instance);
    }
  }, []);

  useEffect(()=>{
    setTranscribedText(activeMeeting.transcript)
  },[activeMeeting])

  const startRecording = () => {
    if (recognitionInstance) {
      setTranscribedText(""); // Clear previous transcription
      recognitionInstance.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (recognitionInstance) {
      recognitionInstance.stop();
      setRecording(false);
    }
  };

  return {
    recording,
    transcribedText,
    startRecording,
    stopRecording
  };
};

export default useAudioRecorder;
