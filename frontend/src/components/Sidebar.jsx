import { useState, useEffect } from 'react';
import {useDispatch,useSelector} from 'react-redux'

import './Sidebar.css'
import { setActiveMeeting,clearActiveMeeting } from '../redux/meetingHistorySlice';
import { openAuthentication,closeAuthentication } from '../redux/authenticationSlice';
import {getMeetings} from '../api/meeting'

import { TbLayoutSidebarLeftCollapse } from "react-icons/tb";
import { FaPenToSquare } from "react-icons/fa6";
import { FaRegUserCircle } from "react-icons/fa";

const Sidebar=({closeSidebar,sidebarVisibility})=>{
    const dispatch=useDispatch();
    const [meetings, setMeetings] = useState([]);
    const activeMeeting = useSelector((state) => state.meetingHistory);

    // Fetch meetings from API on component mount
    useEffect(() => {
        const fetchMeetings  = async () => {
            try {
                const response = await getMeetings();
                setMeetings(response); // Update sidebar with latest meetings
                console.log(meetings)
                if(response.length==0){
                    clearActiveMeetingView ();
                }
            } catch (error) {
                setMeetings([])
                console.error('Error fetching meeting history:', error);
            }
        };

        fetchMeetings ();  // Call the function to load meetings
    }, [activeMeeting]); // Refetch when activeMeeting updates

    // Handle meeting selection
    const handleSelectMeeting = (meeting) => {
        dispatch(setActiveMeeting(meeting));
        console.log(meeting);
    };

    const clearActiveMeetingView =()=>{
        // Reset the active meeting state in Redux to null
        dispatch(clearActiveMeeting());

        closeSidebar();
    }

    // Open the authentication popup box
    const openAuthenticationPopup=()=>{
        dispatch(openAuthentication());
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
                <div className="login-option" onClick={openAuthenticationPopup}>
                    <h3>Login</h3>
                    <FaRegUserCircle className="icon" size={20}/>
                </div>

                <div className="meeting-creation" onClick={clearActiveMeetingView } >
                    <h3>New meeting</h3>
                    <FaPenToSquare className="icon" size={20}/>
                </div>

                <div className="history-option">
                    <h3>My history</h3>
                    <div className="history-list">
                        <ul>
                            {meetings.map((meeting,index)=>(
                                <li className={activeMeeting.id==meeting.id? 'active':''} key={index} onClick={()=>handleSelectMeeting(meeting)}>
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
  