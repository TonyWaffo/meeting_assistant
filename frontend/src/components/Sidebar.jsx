import { useState } from 'react';
import {useDispatch} from 'react-redux'

import './Sidebar.css'
import { setActiveMeeting,clearActiveMeeting } from '../redux/meetingHistorySlice';

import { TbLayoutSidebarLeftCollapse } from "react-icons/tb";
import { FaPenToSquare } from "react-icons/fa6";

const Sidebar=({closeSidebar,sidebarVisibility})=>{
    const dispatch=useDispatch();

    let meetingHistory=[
        {
            id:1,
            topic:'Topic 1111111111111111111111111111111111111111111',
        },
        {
            id:2,
            topic:'Topic 2',
        },
        {
            id:3,
            topic:'Topic 3',
        }
    ];

    const selectMeeting=(meeting)=>{
        //call the useDispatch to set the conversation history thanks to the id selected
        dispatch(setActiveMeeting(meeting))
    }

    const createMeeting=()=>{
        dispatch(clearActiveMeeting())
    }

    return (
      <>
          <section className="sidebar-section">
            <div className="sibebar-header">
                <div>TransMeet</div>
                <div>
                    {sidebarVisibility && <TbLayoutSidebarLeftCollapse size={30} onClick={closeSidebar}/>}
                </div>
            </div>
            <div className="sidebar-features">
                <div className="login-option">
                    <h3>Login</h3>
                </div>

                <div className="meeting-creation">
                    <h3>New meeting</h3>
                    <FaPenToSquare className="new-meeting-icon" size={20} onClick={createMeeting} />
                </div>

                <div className="history-option">
                    <h3>My history</h3>
                    <div className="history-list">
                        <ul>
                            {meetingHistory.map((meeting,index)=>(
                                <li key={index} onClick={()=>selectMeeting(meeting)}>
                                    {meeting.topic}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>

            <div className="contact-links">
                <ul>
                    <li><a href="tel:+1234567890">Support: +1234567890</a></li>
                    <li><a href="https://www.instagram.com/yourprofile" target="_blank" rel="noopener noreferrer">Instagram</a></li>
                    <li><a href="mailto:support@example.com">Email: support@example.com</a></li>
                    <li><a href="https://www.website.com">Website</a></li>
                </ul>
            </div>
          </section>
      </>
    )
  }
  
  export default Sidebar
  