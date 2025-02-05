import Sidebar from "../components/Sidebar"
import Meeting from "../components/Meeting"
import './MeetingAssistant.css'

import { useState } from "react";

import { TbLayoutSidebarLeftExpand } from "react-icons/tb";

const MeetingAssistant=()=>{
  const [sidebarVisibility,setSidebarVisibility]=useState(false);

  const closeSidebar=()=>{
    setSidebarVisibility(false);
  }

  const openSidebar=()=>{
    setSidebarVisibility(true);
  }

  return (
    <>
      <section className="meeting-assistant">
        <div className={`sidebar ${sidebarVisibility ? "" : "closed"}`}>
           <Sidebar closeSidebar={closeSidebar} sidebarVisibility={sidebarVisibility}/>
        </div>
        <div className={`mainframe ${sidebarVisibility ? "blur" : ""}`}>
            <div className="mainframe-header">
                <div>
                {!sidebarVisibility && <TbLayoutSidebarLeftExpand size={30} onClick={openSidebar} />}
                </div>
                <div>Logo</div>
            </div>
            <Meeting/>
        </div>
      </section>
    </>
  )
}

export default MeetingAssistant
