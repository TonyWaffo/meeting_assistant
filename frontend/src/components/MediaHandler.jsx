import { useState, useRef } from "react";
import { useSelector,useDispatch } from "react-redux";
import "./MediaHandler.css";
import useAudioRecorder from "../hooks/useAudioRecorder";
import { sendTranscript } from "../api/meeting"; // Import your sendTranscript function
import { setActiveMeeting,clearActiveMeeting } from "../redux/meetingHistorySlice";


import { IoAddCircle } from "react-icons/io5";
import { FaMicrophone } from "react-icons/fa";


const MediaHandler = () => {
  const { recording, transcribedText, startRecording, stopRecording } = useAudioRecorder();
  const [loading, setLoading] = useState(false);

  const activeMeeting=useSelector((state)=>state.meetingHistory);

  const dispatch=useDispatch();

  const triggerUpload = () => {
    // File input logic here (if needed)
  };

  const processFile = () => {
    setLoading(true);
    // Handle file processing if necessary
    setLoading(false);
  };

  const handleStopRecording = async () => {

    // Wait for few seconds before stopping the recording
    await new Promise(resolve => setTimeout(resolve, 1000)); // ms

    stopRecording(); // Stop recording

    if (transcribedText) {
      try {
        setLoading(true);
        // Call sendTranscript with the transcribed text and meeting ID
        const response = await sendTranscript(transcribedText, activeMeeting.id);
        console.log("Transcript sent successfully:", response);
        
        // If it's a new meeting, update the active meeting
        if (response.meeting && response.meeting.id !== activeMeeting.id) {
            dispatch(setActiveMeeting(response.meeting));  // Update Redux state
            
        }
      } catch (error) {
        console.error("Error sending transcript:", error.message);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="media-handler">
      {/* <div className="media-uploader">
        <IoAddCircle className="upload-icon" size={50} onClick={triggerUpload} />
        <span className="file-instruction">Click to add</span>
      </div>

      <div className="separator">Or record directly</div> */}

      {(!activeMeeting?.transcript || !transcribedText) && <div className="media-recorder">
        <span className="recorder-instruction">
          {recording ? "Press to stop recording" : "Press to start recording"}
        </span>
        <div className="recorder-button">
          <div className={`mic-container ${recording ? "pulsing-circle" : ""}`}>
            <FaMicrophone className="mic-icon" size={30} onClick={recording ? handleStopRecording : startRecording} />
          </div>
        </div>

        {recording && <span className="recording-timer">Recording...</span>}
      </div>}

      {/* <button className="process-audio" onClick={processFile} disabled={loading}>
        {loading ? "Processing..." : "Transcribe Audio"}
      </button> */}

      {(activeMeeting?.transcript || transcribedText) && (
        <div className="transcription-result">
          <h3>Transcribed Text:</h3>
          <p>{activeMeeting?.transcript  || transcribedText}</p>
        </div>
      )}
    </div>
  );
};

export default MediaHandler;
