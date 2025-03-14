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
    const isUserLoggedIn= useSelector((state) => state.authentication.isLoggedIn)

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
    }, [activeMeeting,isUserLoggedIn]); // Refetch when activeMeeting updates

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
                <div className='logo'>Kéré</div>
                <div className='toggle-icon'>
                    {sidebarVisibility && <TbLayoutSidebarLeftCollapse size={30} onClick={closeSidebar}/>}
                </div>
            </div>
            <div className="sidebar-features">
                <div className="login-option" onClick={openAuthenticationPopup}>
                    <h3>Connexion</h3>
                    <FaRegUserCircle className="icon" size={20}/>
                </div>

                <div className="meeting-creation" onClick={clearActiveMeetingView } >
                    <h3>Nouvelle réunion</h3>
                    <FaPenToSquare className="icon" size={20}/>
                </div>

                <div className="history-option">
                    <h3>Historique</h3>
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
                    {/* <li><a href="tel:+1234567890">Support: +1234567890</a></li> */}
                    <li><a href="https://www.instagram.com/b.ease_ci?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==" target="_blank" rel="noopener noreferrer">Instagram</a></li>
                    <li><a href="mailto:b.easeteam@gmail.com">b.easeteam@gmail.com</a></li>
                    {/* <li><a href="https://www.website.com">Website</a></li> */}
                </ul>
            </div>
          </section>
      </>
    )
  }
  
  export default Sidebar
  