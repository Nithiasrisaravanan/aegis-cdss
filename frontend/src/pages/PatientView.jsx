import { useState, useEffect } from 'react'
import axios from 'axios'

export default function PatientView() {
  const [prescriptions, setPrescriptions] = useState([])
  const [selected, setSelected] = useState(null)
  const [tab, setTab] = useState('summary')

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/prescriptions')
      .then(res => {
        setPrescriptions(res.data)
        if (res.data.length > 0) setSelected(res.data[res.data.length - 1])
      })
  }, [])

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-blue-400 mb-1">Patient Prescription Portal</h2>
        <p className="text-gray-400 text-sm">Access your doctor's clinical prescription guidelines and recommended medicines.</p>
      </div>

      {/* Patient Selector */}
      <div className="mb-6">
        <label className="text-gray-400 text-sm mb-2 block">Select Patient Profile</label>
        <select
          className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 w-full"
          onChange={e => {
            const p = prescriptions.find(x => x.id === parseInt(e.target.value))
            setSelected(p)
          }}
          value={selected?.id || ''}
        >
          {prescriptions.map(p => (
            <option key={p.id} value={p.id}>
              {p.patient_name} (Age {p.age}, {p.diagnosis}) - Published {p.issued_on}
            </option>
          ))}
        </select>
      </div>

      {selected ? (
        <>
          {/* Info Cards */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-xs mb-2">PATIENT PROFILE</p>
              <p className="font-bold text-white">{selected.patient_name}</p>
              <p className="text-gray-400 text-sm">Age {selected.age} · {selected.gender}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-xs mb-2">CLINICAL ASSESSMENT</p>
              <p className="font-bold text-blue-400">{selected.diagnosis}</p>
              <p className="text-green-400 text-sm">✓ Verified Prescription</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <p className="text-gray-400 text-xs mb-2">ISSUED ON</p>
              <p className="font-bold text-white">{selected.issued_on}</p>
              <p className="text-green-400 text-sm">● Active Prescription</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-4">
            {['summary', 'medicines'].map(t => (
              <button key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  tab === t ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
                }`}>
                {t === 'summary' ? 'PRESCRIPTION SUMMARY' : 'MEDICINES & STOCKISTS'}
              </button>
            ))}
          </div>

          {tab === 'summary' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <pre className="text-gray-300 text-sm whitespace-pre-wrap font-sans">
                {selected.report}
              </pre>
            </div>
          )}

          {tab === 'medicines' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <p className="text-gray-400 text-sm mb-4">Prescribed medicines:</p>
              <div className="flex flex-wrap gap-2">
                {selected.medicines.map((m, i) => (
                  <span key={i} className="bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm">
                    {typeof m === 'string' ? m : m.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center text-gray-600 py-20">
          No prescriptions found. Publish one from the Doctor view.
        </div>
      )}
    </div>
  )
}