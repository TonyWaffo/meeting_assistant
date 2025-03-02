import { useState, useRef, useEffect } from "react";
import React from 'react';
import { useSelector,useDispatch } from "react-redux";
import "./MediaHandler.css";
import useAudioRecorder from "../hooks/useAudioRecorder";
import { uploadFile } from "../api/meeting";
import { setActiveMeeting,clearActiveMeeting } from "../redux/meetingHistorySlice";


import { IoAddCircle } from "react-icons/io5";
import { FaMicrophone } from "react-icons/fa";


const MediaHandler = () => {
  const { recording, startRecording, stopRecording,audioBlob,audioUrl,clearAudioBlobAndUrl } = useAudioRecorder();
  const [loading, setLoading] = useState(false);
  const [audioFile,setAudioFile]=useState(null);

  const fileRef=useRef(null);

  const activeMeeting=useSelector((state)=>state.meetingHistory);

  const dispatch=useDispatch();

  const triggerUpload = () => {
    fileRef.current?.click();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setAudioFile(file);
  };


  const processFile = async () => {
    setLoading(true);
    let file;

    if(audioFile){
      file=audioFile;
    }else if(audioBlob){
      file=new File([audioBlob], 'recording.mp3', { type: 'audio/mp3' });
    }else{
      setLoading(false);
      return;
    }

    console.log(file);
    
    try {
        const response = await uploadFile(file, activeMeeting?.id);
        console.log('Upload successful:', response);
        dispatch(setActiveMeeting(response.meeting))
        setAudioFile(null);
        clearAudioBlobAndUrl();
      } catch (error) {
        console.error('Upload failed:', error);
    }
          
    setLoading(false);
  };

  const handleStopRecording = async () => {

    // Wait for few seconds before stopping the recording
    // await new Promise(resolve => setTimeout(resolve, 1000)); // ms

    stopRecording(); // Stop recording
  };


  return (
    <div className="media-handler">

      {!activeMeeting?.transcript ?
      (
        <>
          <div className="media-uploader">
            <input type="file" ref={fileRef} onChange={handleFileUpload}/>
            <b> {audioFile ? audioFile?.name : "Cliquez pour ajouter un fichier"}</b>
            <IoAddCircle className="upload-icon" size={50} onClick={triggerUpload} />
            {/* <span className="file-instruction">Click to add</span> */}
          </div>

          <div className="separator">Ou enregistrer directement</div>

          <div className="media-recorder">
            <span className="recorder-instruction">
              {recording ? "Clickez pour arrêter l\'enregistrement" : "Clickez pour commencer l\'enregistrement"}
            </span>
            <div className="recorder-button">
              <div 
                className={`mic-container ${recording ? "pulsing-circle" : ""}`}
                onClick={recording ? handleStopRecording : startRecording}>
                <FaMicrophone className="mic-icon" size={30} />
              </div>
            </div>

            {recording && <span className="recorder-instruction">Recording...</span>}
            {(audioBlob && !recording)  && <span className="recorder-instruction">Meeting enregistré</span>}
          </div>

          <button className={`process-audio ${loading ? "glowing-button" : ""}`} 
            onClick={processFile} disabled={loading}>
            {loading ? "Processing..." : "Transcribe Audio"}
          </button>
        </>
      ):(
        <div className="transcription-result">
          <h3>Transcription</h3>
          <p>{activeMeeting?.transcript.split('\n').map((line, index) => (
            <React.Fragment key={index}>
              {line}
              <br />
              <br/>
            </React.Fragment>
          ))}</p>
        </div>
      ) }

    </div>
  );
};

export default MediaHandler;
