import { useState } from 'react'
import axios from 'axios'

export default function ResultsPanel({ results }) {
  const [tab, setTab] = useState('report')
  const [publishing, setPublishing] = useState(false)
  const [published, setPublished] = useState(false)
  const [patientName, setPatientName] = useState('')
  const [patientAge, setPatientAge] = useState('')
  const [patientGender, setPatientGender] = useState('Male')

  const { prediction, shap, credibility, articles, report, medicines } = results

  const publishPrescription = async () => {
    if (!patientName) return alert('Enter patient name!')
    setPublishing(true)
    try {
      await axios.post('http://127.0.0.1:8000/prescriptions', {
        patient_name: patientName,
        age: parseInt(patientAge) || 0,
        gender: patientGender,
        diagnosis: prediction.primary.label,
        report: report,
        medicines: medicines.map(m => m.name)
      })
      setPublished(true)
    } catch (e) {
      alert('Failed to publish')
    } finally {
      setPublishing(false)
    }
  }

  const tabs = [
    { id: 'report', label: 'REPORT & TREATMENT' },
    { id: 'shap', label: 'SHAP EXPLAIN' },
    { id: 'medicines', label: 'MEDICINES API' },
    { id: 'evidence', label: `NIH EVIDENCE (${articles?.length || 0})` },
  ]

  return (
    <div className="space-y-4">
      {/* Top 3 Cards */}
      <div className="grid grid-cols-3 gap-4">
        {/* Primary Assessment */}
        <div className="bg-gray-900 border border-blue-800 rounded-xl p-4">
          <p className="text-blue-400 text-xs font-bold mb-2">PRIMARY ASSESSMENT</p>
          <p className="text-white font-bold text-lg">{prediction.primary.label}</p>
          <p className="text-3xl font-bold text-blue-400">{prediction.primary.probability}%</p>
          <p className="text-gray-500 text-xs">{prediction.primary.model}</p>
        </div>

        {/* System Confidence */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p className="text-gray-400 text-xs font-bold mb-2">SYSTEM CONFIDENCE</p>
          <p className="text-green-400 font-bold">
            {prediction.confidence.reliable ? '✓ Reliable Index' : '⚠ Low Confidence'}
          </p>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-2 mb-1">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${prediction.confidence.score}%` }}
            />
          </div>
          <p className="text-white font-bold">{prediction.confidence.score}%</p>
          <p className="text-gray-500 text-xs">
            Models {prediction.confidence.models_agree ? 'agree ✓' : 'disagree ⚠'}
          </p>
        </div>

        {/* Differential Diagnosis */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p className="text-gray-400 text-xs font-bold mb-2">DIFFERENTIAL DIAGNOSIS</p>
          {prediction.differential.map((d, i) => (
            <div key={i} className="flex justify-between items-center mb-1">
              <span className="text-gray-300 text-sm">{d.label}</span>
              <span className="text-blue-400 font-bold text-sm">{d.probability}%</span>
            </div>
          ))}
          <div className="mt-2 border-t border-gray-700 pt-2">
            <p className="text-gray-500 text-xs">Consider also:</p>
            <p className="text-gray-400 text-xs">• Stable Angina Pectoris</p>
            <p className="text-gray-400 text-xs">• Hypertensive Heart Disease</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 flex-wrap">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.id ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

        {/* REPORT TAB */}
        {tab === 'report' && (
          <div>
            <h3 className="text-blue-400 font-bold mb-4">Clinical Report & Treatment</h3>
            <div className="prose prose-invert max-w-none">
              <pre className="text-gray-300 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                {report}
              </pre>
            </div>

            {/* Publish Prescription */}
            <div className="mt-6 border-t border-gray-700 pt-4">
              <h4 className="text-yellow-400 font-bold mb-3">📋 Publish Prescription to Patient Portal</h4>
              <div className="grid grid-cols-3 gap-3 mb-3">
                <input
                  placeholder="Patient Name"
                  value={patientName}
                  onChange={e => setPatientName(e.target.value)}
                  className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                />
                <input
                  placeholder="Age"
                  type="number"
                  value={patientAge}
                  onChange={e => setPatientAge(e.target.value)}
                  className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                />
                <select
                  value={patientGender}
                  onChange={e => setPatientGender(e.target.value)}
                  className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
                >
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
                </select>
              </div>
              <button
                onClick={publishPrescription}
                disabled={publishing || published}
                className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 text-white font-bold px-6 py-2 rounded-lg transition-all"
              >
                {published ? '✓ Published!' : publishing ? 'Publishing...' : 'Publish Prescription'}
              </button>
            </div>
          </div>
        )}

        {/* SHAP TAB */}
        {tab === 'shap' && (
          <div>
            <h3 className="text-blue-400 font-bold mb-1">SHAP Feature Contributions</h3>
            <p className="text-gray-400 text-xs mb-4">
              Calculates how each clinical input feature pushed the model's likelihood for {prediction.primary.label}
            </p>
            <div className="flex gap-4 mb-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-yellow-500 inline-block"/>
                Pushes risk up (Positive)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-teal-500 inline-block"/>
                Protective / Pushes risk down (Negative)
              </span>
            </div>

            {/* SHAP Bars */}
            <div className="space-y-2 mb-6">
              {shap.features.map((f, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-gray-400 text-xs w-24 text-right shrink-0">{f.feature}</span>
                  <div className="flex-1 bg-gray-800 rounded h-6 relative overflow-hidden">
                    <div
                      className={`h-full rounded ${f.direction === 'up' ? 'bg-yellow-500' : 'bg-teal-500'}`}
                      style={{ width: `${Math.min(Math.abs(f.value) * 300, 100)}%` }}
                    />
                  </div>
                  <span className={`text-xs w-16 ${f.direction === 'up' ? 'text-yellow-400' : 'text-teal-400'}`}>
                    {f.value > 0 ? '+' : ''}{f.value}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-gray-500 text-xs">*Base value (model intercept): {shap.base_value}</p>

            {/* Credibility Table */}
            {credibility && credibility.length > 0 && (
              <div className="mt-6">
                <h4 className="text-yellow-400 font-bold mb-3">Evidence-Validated Credibility Scores</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 text-xs border-b border-gray-700">
                        <th className="text-left py-2">Feature</th>
                        <th className="text-left py-2">SHAP Impact</th>
                        <th className="text-left py-2">Credibility %</th>
                        <th className="text-left py-2">Citation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {credibility.map((c, i) => (
                        <tr key={i} className="border-b border-gray-800">
                          <td className="py-2 text-white">
                            {c.flagged && <span className="text-yellow-400 mr-1">⚠</span>}
                            {c.feature}
                          </td>
                          <td className={`py-2 ${c.shap_value > 0 ? 'text-yellow-400' : 'text-teal-400'}`}>
                            {c.shap_value > 0 ? '+' : ''}{c.shap_value}
                          </td>
                          <td className="py-2">
                            <span className={`font-bold ${
                              c.credibility_pct > 60 ? 'text-green-400' :
                              c.credibility_pct > 40 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {c.credibility_pct}%
                            </span>
                          </td>
                          <td className="py-2">
                            {c.citation_url ? (
                              <a href={c.citation_url} target="_blank" rel="noreferrer"
                                className="text-blue-400 hover:underline text-xs">
                                {c.citation_label?.substring(0, 40)}...
                              </a>
                            ) : (
                              <span className="text-gray-500 text-xs">{c.citation_label}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MEDICINES TAB */}
        {tab === 'medicines' && (
          <div>
            <h3 className="text-blue-400 font-bold mb-1">Suggested Healthcare Products & Stockists</h3>
            <p className="text-gray-400 text-xs mb-4">Medicine recommendations and pharmacy locations in India</p>
            <div className="space-y-4">
              {medicines.map((m, i) => (
                <div key={i} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="text-white font-bold">{m.name}</p>
                      <p className="text-gray-400 text-xs">Agency: {m.agency} | Country: {m.country}</p>
                      <p className="text-gray-400 text-xs">Code: {m.code}</p>
                    </div>
                    <a href={m.leaflet_url} target="_blank" rel="noreferrer"
                      className="bg-blue-700 hover:bg-blue-600 text-white text-xs px-3 py-1.5 rounded-lg">
                      📄 Retrieve Leaflets
                    </a>
                  </div>
                  <div className="mt-3">
                    <p className="text-gray-400 text-xs mb-1 font-bold">LOCAL STOCKISTS</p>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {m.stockists.map((s, j) => (
                        <span key={j} className="bg-green-900 text-green-300 text-xs px-2 py-1 rounded-full">{s}</span>
                      ))}
                    </div>
                    <p className="text-gray-400 text-xs mb-1 font-bold">ALTERNATIVE BRANDS (INDIA)</p>
                    <div className="flex flex-wrap gap-2">
                      {m.indian_brands.map((b, j) => (
                        <span key={j} className="bg-purple-900 text-purple-300 text-xs px-2 py-1 rounded-full">{b}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* NIH EVIDENCE TAB */}
        {tab === 'evidence' && (
          <div>
            <h3 className="text-blue-400 font-bold mb-1">Retrieved NIH PubMed Literature</h3>
            <p className="text-gray-400 text-xs mb-4">
              Verifiable publications embedded and ranked using dynamic FAISS vector search
            </p>
            <div className="space-y-4">
              {articles?.map((a, i) => (
                <div key={i} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-white font-medium text-sm flex-1 mr-4">{a.title}</p>
                    <span className="bg-blue-900 text-blue-300 text-xs px-2 py-1 rounded-full shrink-0">
                      {a.relevance}%
                    </span>
                  </div>
                  <p className="text-gray-400 text-xs mb-2">
                    {a.journal} · {a.year} · PMID: {a.pmid}
                  </p>
                  <p className="text-gray-300 text-xs mb-3 leading-relaxed">
                    {a.abstract?.substring(0, 300)}...
                  </p>
                  <a href={a.url} target="_blank" rel="noreferrer"
                    className="bg-blue-700 hover:bg-blue-600 text-white text-xs px-3 py-1.5 rounded-lg inline-block">
                    🔗 PubMed Link
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}