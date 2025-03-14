import { useState,useRef, useEffect } from 'react';
import {useDispatch,useSelector} from 'react-redux'

import MediaHandler from "./MediaHandler"
import './Meeting.css'
import { setActiveMeeting,clearActiveMeeting } from '../redux/meetingHistorySlice';
//update the meeting history and the active meeting
import { sendMessage,getMeetingDetails } from '../api/meeting';

import { IoSendSharp } from "react-icons/io5";

const Meeting=()=>{
    const dispatch=useDispatch()
    const [file,setFile]=useState("");
    const [transcript,setTranscript]=useState("");
    const [conversations,setConversations]=useState(null);
    const [loadingResponse,setLoadingResponse]=useState("");
    const [messageContent, setMessageContent] = useState(""); // New state for message input

    const queryTextAreaRef=useRef(null);
    const messagesEndRef=useRef(null)

    const activeMeeting=useSelector((state)=>state.meetingHistory);


    // Function to fetch meeting details (conversation & transcript)
    const fetchMeetingDetails = async () => {
        if (activeMeeting.id) {
            try {
                const details = await getMeetingDetails(activeMeeting.id);
                setConversations(details.messages || []);
            } catch (error) {
                console.error("Error fetching meeting details:", error);
            }
        }else{
            setConversations([]);
        }
    };

    useEffect(() => {
        fetchMeetingDetails();
        setMessageContent("");
        setLoadingResponse(false);
    }, [activeMeeting]);

    useEffect(()=>{
        if(messagesEndRef.current){
            messagesEndRef.current.scrollIntoView({behavior:"smooth"});
        }
    },[conversations])


    const handleInputChange=(event)=>{
        const textArea=queryTextAreaRef.current;

        if(event.target.value.trim()==""){
            textArea.style.height="200px";
        }
    }

    const handleSendMessage = async (goal='questionAnswer') => {
        /**
         * checck if the user is logged in , otherwise, show th elogin popup
         */
        if (!messageContent.trim() && goal.trim()!='summary') return; // Don't send empty messages

        let message;
        if(goal=='summary'){
            message='Faites moi un resume du recit s\'il te plait '
        }else{
            message=messageContent;
        }

        setLoadingResponse(true); // Show loading while sending

        try {
            const topic = "question_answer" || 'transcription'; // Default to 'transcription' if topic is not set
            const response = await sendMessage(message, activeMeeting.id, topic);
        
            // If it's a new meeting, update the active meeting
            if (response.meeting && response.meeting.id !== activeMeeting.id) {
                dispatch(setActiveMeeting(response.meeting));  // Update Redux state
            }

            setMessageContent("");

            // Fetch updated messages from the backend (including system response)
            fetchMeetingDetails();

        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setLoadingResponse(false); // Hide loading
        }
    };


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
                <h2>Ton assistant de réunion</h2>
                {/*This part is ony viewable when the user create a new recording, not available in history and if the audio hasn't been processed yet*/}
                <MediaHandler/>

                {/* Only available when audio file is selected and trancribed button is pressed and when summary or text present in the history */}
                <div className="meeting-content">
                    {/* if no transcript and no transcript */}
                    {(!activeMeeting.transcript && !conversations) && <p>Téléchargez un fichier ou enregistrez la réunion</p>}

                    {/* if there is a file or histiry being processed, implement a spinning animation */}
                    

                    {/* If there is either a transcript available or a conversation history */}
                    { (activeMeeting.transcript || conversations) && conversations?.map((message,index)=>(
                        <div key={index} className={`conversation ${message.is_user==true ? "user":"system"}`}>
                            <b>{message.is_user==true ? "Moi":"Kéré"}</b><br/>
                            {/* <i>{(message.topic).charAt(0).toUpperCase() + (message.topic).slice(1)}</i> */}
                            <p dangerouslySetInnerHTML={{ __html: message?.content }}></p>
                        </div>
                    ))}
                    <div ref={messagesEndRef} /> {/* Scroll target */}

                </div>
            </div>


            <div className="query-container"> 
                <textarea className="query-input" 
                    ref={queryTextAreaRef} 
                    value={messageContent}
                    onInput={handleInputChange}
                    onChange={(e) => setMessageContent(e.target.value)}
                    // disabled={!activeMeeting.transcript }
                    readOnly={!activeMeeting.transcript || loadingResponse}
                    placeholder={activeMeeting.transcript ? 'Posez une question sur le meeting' : 'Faites un enregistrement pour utiliser le chat'}>
                </textarea>

                <div className="query-actions">
                    {/* Hide this part when the response is loading */}
                    {/* Gray out these elements when no transcript is available  */}
                    {!loadingResponse && 
                        <div className='query-buttons'>
                            <div>
                                {/* <button
                                    disabled={!activeMeeting.transcript} // Disable if no transcription
                                    className={!activeMeeting.transcript ? 'disabled-button' : ''}>Transcription
                                </button> */}
                                <button
                                    disabled={!activeMeeting.transcript} // Disable if no transcription
                                    className={!activeMeeting.transcript ? 'disabled-button' : ''}
                                    onClick={()=>handleSendMessage('summary')}>Resumé
                                </button>
                            </div>
                            <div>
                                {activeMeeting.transcript && <IoSendSharp className='send-icon' size={30}
                                    onClick={() => handleSendMessage()}
                                 />} {/* sending icon is disabled if the text area is empty or the response is loading */}
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
  