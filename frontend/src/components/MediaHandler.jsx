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
  const [uploadError,setUploadError]=useState(null);

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
    console.log("file uplaoded",file)

    // Remove the audio recorded when a file is downloaded
    clearAudioBlobAndUrl()
  };


  const processFile = async () => {

    if(loading){
      return;       // Make sure no other file us trying to be processed when another one is already processing
    }

    
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

    if(file.size< 614400){
      const errorMessage = `Audio trop court. Minimum: 600 KB, Soumis: ${(file.size / 1024).toFixed(2)} KB`;
      setUploadError(errorMessage);
    
      // Automatically remove the error after 15 seconds
      setTimeout(() => {
        setUploadError('');
      }, 15000);

      setLoading(false);
      return 
    }
    setUploadError('')

    console.log(file);
    
    try {
        const response = await uploadFile(file, activeMeeting?.id);
        console.log('Upload successful:', response);
        dispatch(setActiveMeeting(response.meeting))
        setAudioFile(null);
        clearAudioBlobAndUrl();
      } catch (error) {
        console.error('Upload failed:', error);
        setUploadError(error)
    }
          
    setLoading(false);
  };

  const handleStopRecording = async () => {

    // Wait for few seconds before stopping the recording
    // await new Promise(resolve => setTimeout(resolve, 1000)); // ms

    stopRecording(); // Stop recording
    setAudioFile(null); // Remove any uploaded file when recording is stopped
    console.log("should clear the file download",audioFile);
  };


  return (
    <div className="media-handler">
      {uploadError && (
        <div className={`upload-error ${uploadError ? 'visible' : ''}`}>
          {uploadError}
        </div>
      )}

      {!activeMeeting?.transcript ?
      (
        <>
          <div className="media-uploader">
            <input type="file" ref={fileRef} onChange={handleFileUpload}/>
            <b> {audioFile ? audioFile?.name : "Cliquez pour ajouter votre réunion"}</b>
            <IoAddCircle className="upload-icon" size={50} onClick={triggerUpload} />
            {/* <span className="file-instruction">Click to add</span> */}
          </div>

          <div className="separator">Ou enregistrez directement</div>

          <div className="media-recorder">
            <span className="recorder-instruction">
              {recording ? "Cliquez pour arrêter l\'enregistrement" : "Cliquez pour commencer l\'enregistrement"}
            </span>
            <div className="recorder-button">
              <div 
                className={`mic-container ${recording ? "pulsing-circle" : ""}`}
                onClick={recording ? handleStopRecording : startRecording}>
                <FaMicrophone className="mic-icon" size={30} />
              </div>
            </div>

            {recording && <span className="recorder-instruction">En train d'enregistrer...</span>}
            {(audioBlob && !recording)  && <span className="recorder-instruction">Meeting enregistré</span>}
          </div>
          <button className={`process-audio ${loading ? "glowing-button" : ""}`} 
            onClick={processFile} disabled={loading}>
            {loading ? "En traitement..." : "Transcris l\'audio"}
          </button>
        </>
      ):(
        <div className="transcription-result">
          <h3>Transcription</h3>
          {/* Because the transcript is already formatted in a specific format coming from the backend */}
          <p dangerouslySetInnerHTML={{ __html: activeMeeting?.transcript }}></p>

        </div>
      ) }

    </div>
  );
};

export default MediaHandler;
