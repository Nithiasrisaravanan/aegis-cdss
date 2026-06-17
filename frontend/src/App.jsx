import { useState } from 'react'
import DoctorView from './pages/DoctorView'
import PatientView from './pages/PatientView'

export default function App() {
  const [view, setView] = useState('doctor')

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top Bar */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-blue-400 font-bold text-xl">⚕ Aegis CDSS</span>
          <span className="text-gray-500 text-sm">ML + RAG</span>
        </div>
        <div className="flex bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setView('doctor')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
              view === 'doctor'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            DOCTOR
          </button>
          <button
            onClick={() => setView('patient')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
              view === 'patient'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            PATIENT
          </button>
        </div>
        <div className="text-gray-400 text-sm">Clinical Assistant</div>
      </header>

      {/* Main Content */}
      {view === 'doctor' ? <DoctorView /> : <PatientView />}

      {/* Disclaimer */}
      <div className="text-center text-xs text-gray-600 py-2 border-t border-gray-800">
        ⚠ Decision support only — clinician makes final diagnosis
      </div>
    </div>
  )
}