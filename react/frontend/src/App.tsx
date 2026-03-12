import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import ProcessNetwork from './pages/ProcessNetwork'
import DefectTracing from './pages/DefectTracing'
import FiveWhys from './pages/FiveWhys'
import RiskAnalysis from './pages/RiskAnalysis'
import About from './pages/About'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="network" element={<ProcessNetwork />} />
        <Route path="defects" element={<DefectTracing />} />
        <Route path="five-whys" element={<FiveWhys />} />
        <Route path="risk" element={<RiskAnalysis />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  )
}

export default App
