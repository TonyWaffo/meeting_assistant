import MediaHandler from "./MediaHandler"

const Meeting=()=>{
    let conversations=[
        {
            speaker:'user',
            subject:"Transcription",
            content:""
        },
        {
            speaker:'system',
            subject:"Transcription",
            content:"........"
        },
        {
            speaker:'user',
            subject:"Summary",
            content:""
        },
        {
            speaker:'system',
            subject:"Summary",
            content:"........"
        },
        {
            speaker:'user',
            subject:"Q&A",
            content:""
        },
        {
            speaker:'system',
            subject:"Q&A",
            content:"........"
        },
    ]
    return (
      <>
          <section className="meeting-section">
            <h2>Your meeting assistant</h2>
            {/*This part is ony viewable when the user create a new recording, not available in history and if the audio hasn't been processed yet*/}
            <MediaHandler/>

            {/* Only available when audio file is selected and trancribed button is pressed and when summary or text present in the history */}
            <div className="meeting-content">
                {/* if no file is processe */}
                <p>Load and process your file </p>
                {/* If there  the file is already processed, show the chat */}
                {conversations.map((conversation,index)=>(
                    <div className="conversation">
                        <span>{conversation.speaker}</span>
                        <b>{conversation.subject}</b>
                        <p>{conversation.content}</p>
                    </div>
                ))}

            </div>


            <div className="querybox"> 
                <textarea className="querybox-input">

                </textarea>

                <div>
                    {/* Hide this part when the response is loading */}
                    {/* Gray out these elements when no audio file is available  */}
                    <>
                        <button>Transcription</button>
                        <button>Resumer</button>
                        <i>Icon d'envoi</i> {/* sending icon is grayed out if the text area is empty or the response is loading */}
                    </>

                    <>
                    {/* Create an animation when the response is loading  */}
                        <div className="query-box-loading">
                            ...
                        </div>
                    </>
                </div>
            </div>
          </section>
      </>
    )
  }
  
  export default Meeting
  