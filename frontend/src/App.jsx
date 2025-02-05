import { useState } from 'react'
import {Routes,Route} from 'react-router-dom'
import MeetingAssistant from './pages/MeetingAssistant'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Routes>
        <Route path="/" element={<MeetingAssistant/>}/>
      </Routes>
    </>
  )
}

export default App
