import Sidebar from "../components/Sidebar"
import Meeting from "../components/Meeting"
import Authentication from "../components/Authentication";
import { openAuthentication,closeAuthentication } from "../redux/authenticationSlice";
import './MeetingAssistant.css'

import bEaseLogo from '/images/logo_bEase_noBg450_200.png'

import { useState } from "react";
import { useSelector } from "react-redux";

import { TbLayoutSidebarLeftExpand } from "react-icons/tb";

const MeetingAssistant=()=>{
  const [sidebarVisibility,setSidebarVisibility]=useState(false);

  const isAuthenticationPopupOpen=useSelector((state)=>state.authentication.isOpen);

  const closeSidebar=()=>{
    setSidebarVisibility(false);
  }

  const openSidebar=()=>{
    setSidebarVisibility(true);
  }

  return (
    <>
      <Authentication />
      <section className={`meeting-assistant ${isAuthenticationPopupOpen ? "blur" : ""}`}>
        <div className={`sidebar ${sidebarVisibility ? "" : "closed"}`}>
           <Sidebar closeSidebar={closeSidebar} sidebarVisibility={sidebarVisibility}/>
        </div>
        <div className={`mainframe ${sidebarVisibility ? "blur" : ""}`}>
            <div className="mainframe-header">
                <div>
                {!sidebarVisibility && <TbLayoutSidebarLeftExpand size={30} onClick={openSidebar} />}
                </div>
                <div>
                  <img src={bEaseLogo}></img>
                </div>
            </div>
            <Meeting/>
        </div>
      </section>
    </>
  )
}

export default MeetingAssistant
