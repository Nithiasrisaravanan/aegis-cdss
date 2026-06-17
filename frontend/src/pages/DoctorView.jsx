import { useState } from 'react'
import axios from 'axios'
import PatientForm from '../components/PatientForm'
import ResultsPanel from '../components/ResultsPanel'

export default function DoctorView() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('http://127.0.0.1:8000/analyze', formData)
      setResults(res.data)
    } catch (err) {
      setError('Analysis failed. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex gap-4 p-4 min-h-screen">
      {/* Left Panel */}
      <div className="w-80 shrink-0">
        <PatientForm onSubmit={handleSubmit} loading={loading} />
      </div>

      {/* Right Panel */}
      <div className="flex-1">
        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        {loading && (
          <div className="flex flex-col items-center justify-center h-96 gap-4">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400"/>
            <p className="text-gray-400">Running ML pipeline + fetching evidence...</p>
          </div>
        )}
        {results && !loading && (
          <ResultsPanel results={results} />
        )}
        {!results && !loading && (
          <div className="flex flex-col items-center justify-center h-96 text-gray-600">
            <span className="text-6xl mb-4">⚕</span>
            <p className="text-lg">Enter patient data and click Evaluate Symptoms</p>
          </div>
        )}
      </div>
    </div>
  )
}