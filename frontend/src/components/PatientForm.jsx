import { useState } from 'react'

const FIELDS = [
  { key: 'age', label: 'Age', min: 1, max: 120, step: 1, default: 55 },
  { key: 'trestbps', label: 'Resting BP (mmHg)', min: 80, max: 220, step: 1, default: 130 },
  { key: 'chol', label: 'Cholesterol (mg/dL)', min: 100, max: 600, step: 1, default: 240 },
  { key: 'thalach', label: 'Max Heart Rate', min: 60, max: 220, step: 1, default: 150 },
  { key: 'oldpeak', label: 'ST Depression', min: 0, max: 10, step: 0.1, default: 1.0 },
]

const SELECTS = [
  { key: 'sex', label: 'Sex', options: [{ v: 1, l: 'Male' }, { v: 0, l: 'Female' }] },
  { key: 'cp', label: 'Chest Pain Type', options: [
    { v: 0, l: 'Typical Angina' }, { v: 1, l: 'Atypical Angina' },
    { v: 2, l: 'Non-anginal' }, { v: 3, l: 'Asymptomatic' }
  ]},
  { key: 'fbs', label: 'Fasting Blood Sugar >120', options: [{ v: 0, l: 'No' }, { v: 1, l: 'Yes' }] },
  { key: 'restecg', label: 'Resting ECG', options: [
    { v: 0, l: 'Normal' }, { v: 1, l: 'ST-T Abnormality' }, { v: 2, l: 'LV Hypertrophy' }
  ]},
  { key: 'exang', label: 'Exercise Angina', options: [{ v: 0, l: 'No' }, { v: 1, l: 'Yes' }] },
  { key: 'slope', label: 'ST Slope', options: [
    { v: 0, l: 'Upsloping' }, { v: 1, l: 'Flat' }, { v: 2, l: 'Downsloping' }
  ]},
  { key: 'ca', label: 'Major Vessels (0-3)', options: [
    { v: 0, l: '0' }, { v: 1, l: '1' }, { v: 2, l: '2' }, { v: 3, l: '3' }
  ]},
  { key: 'thal', label: 'Thalassemia', options: [
    { v: 1, l: 'Normal' }, { v: 2, l: 'Fixed Defect' }, { v: 3, l: 'Reversible Defect' }
  ]},
]

export default function PatientForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    age: 55, sex: 1, cp: 1, trestbps: 130, chol: 240,
    fbs: 0, restecg: 0, thalach: 150, exang: 0,
    oldpeak: 1.0, slope: 1, ca: 0, thal: 2
  })
  const [notes, setNotes] = useState('')

  const handleChange = (key, value) => {
    setForm(prev => ({ ...prev, [key]: parseFloat(value) }))
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 h-full overflow-y-auto">
      <h2 className="text-blue-400 font-bold text-sm mb-1">PATIENT INTAKE PROFILE</h2>
      <p className="text-gray-500 text-xs mb-4">Enter clinical symptoms and demographic metrics</p>

      {/* Numeric Fields */}
      <div className="space-y-3 mb-4">
        {FIELDS.map(f => (
          <div key={f.key}>
            <label className="text-gray-400 text-xs mb-1 block">{f.label}</label>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={f.min} max={f.max} step={f.step}
                value={form[f.key]}
                onChange={e => handleChange(f.key, e.target.value)}
                className="flex-1 accent-blue-500"
              />
              <span className="text-white text-sm w-12 text-right">{form[f.key]}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Select Fields */}
      <div className="space-y-2 mb-4">
        {SELECTS.map(s => (
          <div key={s.key}>
            <label className="text-gray-400 text-xs mb-1 block">{s.label}</label>
            <select
              value={form[s.key]}
              onChange={e => handleChange(s.key, e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg px-2 py-1.5"
            >
              {s.options.map(o => (
                <option key={o.v} value={o.v}>{o.l}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {/* Medical History */}
      <div className="mb-4">
        <label className="text-gray-400 text-xs mb-1 block">MEDICAL HISTORY (optional)</label>
        <textarea
          value={notes}
          onChange={e => setNotes(e.target.value)}
          rows={3}
          placeholder="Previous conditions, medications, allergies..."
          className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg px-3 py-2 resize-none"
        />
      </div>

      <button
        onClick={() => onSubmit(form)}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-bold py-3 rounded-xl transition-all"
      >
        {loading ? 'Analyzing...' : '⚕ Evaluate Symptoms'}
      </button>
    </div>
  )
}