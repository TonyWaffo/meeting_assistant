import { useState,useRef, useEffect } from 'react';
import {useDispatch,useSelector} from 'react-redux'

import MediaHandler from "./MediaHandler"
import './Meeting.css'
import { setActiveMeeting,clearActiveMeeting } from '../redux/meetingHistorySlice';

import { IoSendSharp } from "react-icons/io5";

const Meeting=()=>{
    const [file,setFile]=useState("");
    const [transcript,setTranscript]=useState("jgh");
    const [conversationHistory,setConversationHistory]=useState(null);
    const [loadingResponse,setLoadingResponse]=useState("");

    const queryTextAreaRef=useRef(null);

    const activeMeeting=useSelector((state)=>state.meetingHistory);

    useEffect(()=>{
        // alert(activeMeeting.topic);
        // if actuualMeeting.is is not null call the api to get the conversation associated with the id of the active meeting
        // and then set the conversations to the one found
    },[activeMeeting])

    let conversations=[
        {
            speaker:'user',
            subject:"Transcription",
            content:"hhjijijlj"
        },
        {
            speaker:'system',
            subject:"Transcription",
            content:".... ,nk.mk...."
        },
        {
            speaker:'user',
            subject:"Summary",
            content:"jhjjijk"
        },
        {
            speaker:'system',
            subject:"Summary",
            content:"...jnjlkjhkhkjhkhkhbkbhbhjbjhbjhbjhbjhbhjb....."
        },
        {
            speaker:'user',
            subject:"Q&A",
            content:"ohhjohuhiuhiug"
        },
        {
            speaker:'system',
            subject:"Q&A",
            content:"........"
        },
    ]

    const handleInputChange=(event)=>{
        const textArea=queryTextAreaRef.current;

        if(event.target.value.trim()==""){
            textArea.style.height="200px";
        }
    }

    /**
     * Create a useEffect hooks that upload the meeting content based on the
     * meeting history(or not).
     * Meaning if a new meeting is created the component will be fresh
     * Might use axios to call the function: if a new meeting  is created
     * , conversation, file, transcript and loading response are null, else
     * set accordingly, use the hooks to update the conversation for persistence
     * 
     */

    return (
      <>
          <section className="meeting-section">
            <div className='meeting-wrapper'>
            <h2>Your meeting assistant</h2>
                {/*This part is ony viewable when the user create a new recording, not available in history and if the audio hasn't been processed yet*/}
                <MediaHandler/>

                {/* Only available when audio file is selected and trancribed button is pressed and when summary or text present in the history */}
                <div className="meeting-content">
                    {/* if no transcript and no transcript */}
                    {(!transcript && !conversationHistory) && <p>Process your file upload or meeting record </p>}

                    {/* if there is a file or histiry being processed, implement a spinning animation */}
                    

                    {/* If there is either a transcript available or a conversation history */}
                    { (transcript || conversationHistory) && conversations.map((conversation,index)=>(
                        <div className={`conversation ${conversation.speaker=="system" ? "system":"user"}`}>
                            <span>{conversation.speaker}</span>
                            <b>{conversation.subject}</b>
                            <p>{conversation.content}</p>
                        </div>
                    ))}

                </div>
            </div>


            <div className="query-container"> 
                <textarea className="query-input" 
                    ref={queryTextAreaRef} 
                    onChange={handleInputChange}
                    placeholder='Posez une question sur le meeting'>

                </textarea>

                <div className="query-actions">
                    {/* Hide this part when the response is loading */}
                    {/* Gray out these elements when no transcript is available  */}
                    {!loadingResponse && 
                        <div className='query-buttons'>
                            <div>
                                <button>Transcription</button>
                                <button>Resumer</button>
                            </div>
                            <div>
                                <IoSendSharp size={30} /> {/* sending icon is grayed out if the text area is empty or the response is loading */}
                            </div>
                        </div>
                    }

                    {/* Create an animation when the response is loading  */}


                    {loadingResponse && 
                        <div className="query-loading">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    }
                </div>
            </div>
          </section>
      </>
    )
  }
  
  export default Meeting
  