import { useState,useRef, useEffect } from 'react';

import './MediaHandler.css'
import useAudioRecorder from '../hooks/useAudioRecorder';
import { formatTime } from '../utils/timeUtils';
import { uploadFile } from '../api/meeting';

import { IoAddCircle } from "react-icons/io5";
import { FaMicrophone } from "react-icons/fa";

const MediaHandler=()=>{
    const {recording,
        audioBlob,
        audioUrl, 
        startRecording, 
        stopRecording
    }=useAudioRecorder();
    const [duration,setDuration]=useState(0);
    const [inputFile,setInputFile]=useState(null);
    const fileInputRef=useRef(null);

    const triggerUpload=()=>{
        fileInputRef.current.click();
    }

    const changeFile=(event)=>{
        const file=event.target.files[0];
        setInputFile(file);
    }

    const processFile=()=>{
        if (audioBlob) {
            uploadFile(audioBlob).then((data) => {
                console.log("Audio uploaded successfully:", data);
            }).catch((error) => {
                console.error("Audio upload failed:", error);
            });
        }
    }

    useEffect(()=>{
        let interval;
        if(recording){
            interval=setInterval(()=>{
                setDuration((prev)=>prev+1); // Increment timer every second
            },1000)
        }else{
            clearInterval(interval);  // Clear interval when recording stops
            setDuration(0);
        }

        // Cleanup interval when the component unmounts
        return ()=>clearInterval(interval);
    },[recording])

    return(
        <>
        <div className="media-handler">
            <div className="media-uploader">
                <IoAddCircle className="upload-icon" size={50} onClick={triggerUpload} />
                <input type="file" style={{display:'none'}} ref={fileInputRef} onChange={changeFile} className="file-input"/>
                <span className="file-name">{ inputFile? inputFile.name: "Pas de fichier selectionne"}</span>

                {/* Only available for new users */}

                {/* If a file is loaded: click to change file; if not, click to upload */}
                <span className="file-instruction">
                    {inputFile ? "Cliquez pour changer" :"Cliquez pour ajouter"}
                </span>
            </div>

            <div className="separator">Or record directly</div>

            <div className="media-recorder">
                <span className="recorder-instruction">{recording? "Press to stop recording" :"Press to start recording"}</span>
                <div className="recorder-button">
                    <div className={`mic-container ${recording ? 'pulsing-circle' : ''}`}>
                        <FaMicrophone className="mic-icon" size={30} onClick={recording ? stopRecording:startRecording} />
                    </div>
                </div> 

                {audioUrl && !recording && (
                <div>
                    <audio controls>
                    <source src={audioUrl} type="audio/wav" />
                    Your browser does not support the audio element.
                    </audio>
                </div>
                )}
                
                {/* Rounded div pulsing and changing color when on */}
                {recording && 
                    <span className="recording-timer">{formatTime(duration)}</span>
                }
            </div>

            <button className="process-audio" onClick={processFile}>Process audio</button>
            
        </div>

        </>
    )
}

export default MediaHandler