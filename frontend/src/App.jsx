import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Detector from './pages/Detector'
import Results from './pages/Results'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import Assistant from './pages/Assistant'
import Admin from './pages/Admin'
import Login from './pages/Login'

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/detect" element={<Detector />} />
        <Route path="/results/:id" element={<Results />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/assistant/:smsId" element={<Assistant />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/login" element={<Login />} />
      </Routes>
      <Footer />
    </>
  )
}
