import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { smsAPI } from '../api/client'
import SecurityGauge from '../components/SecurityGauge'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

export default function Results() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [feedbackSent, setFeedbackSent] = useState('')

  useEffect(() => {
    smsAPI.getDetail(id).then(({ data: d }) => {
      setData(d)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  const handleFeedback = async (type) => {
    try {
      await smsAPI.feedback({ sms_id: parseInt(id), feedback: type })
      setFeedbackSent(type)
    } catch {
      alert('Please login to submit feedback.')
    }
  }

  if (loading) return <div className="loading-spinner"><div className="spinner-border text-success" /></div>
  if (!data) return <div className="container page-container"><p>Message not found.</p></div>

  const xaiChart = data.xai_data?.chart_data
  const chartData = xaiChart ? {
    labels: xaiChart.labels,
    datasets: [{
      label: 'Word Impact',
      data: xaiChart.values,
      backgroundColor: '#7c5cfc',
      borderRadius: 4,
    }],
  } : null

  return (
    <div className="page-container">
      <div className="container">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Analysis Results</h2>
          <Link to={`/assistant/${id}`} className="btn btn-outline-hsds btn-sm">Ask AI Assistant</Link>
        </div>

        <div className="row g-4">
          <div className="col-lg-8">
            <div className="card card-hsds p-4 mb-4">
              <h6 className="text-muted mb-2">Original Message</h6>
              <p className="mb-0">{data.message}</p>
              {data.language !== 'en' && (
                <small className="text-muted">Language: {data.language?.toUpperCase()}</small>
              )}
            </div>

            <div className="card card-hsds p-4 mb-4">
              <div className="d-flex align-items-center gap-3 mb-3">
                <h4 className="mb-0">Classification:</h4>
                <span className={`badge ${data.prediction === 'spam' ? 'badge-spam' : 'badge-ham'} fs-6`}>
                  {data.prediction.toUpperCase()}
                </span>
                <span className="text-muted">Confidence: {(data.confidence * 100).toFixed(1)}%</span>
              </div>

              {data.fraud_type && (
                <div className="alert alert-warning py-2">
                  <strong>Fraud Type:</strong> {data.fraud_type}
                </div>
              )}

              <h6>Reasons:</h6>
              <ul className="mb-0">
                {(data.explanation?.reasons || []).map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>

            {data.phishing_analysis?.analyses?.length > 0 && (
              <div className="card card-hsds p-4 mb-4">
                <h5 className="mb-3">🔗 Phishing URL Analysis</h5>
                {data.phishing_analysis.analyses.map((a, i) => (
                  <div key={i} className="mb-3 p-3 rounded analysis-box">
                    <div className="d-flex justify-content-between">
                      <code className="small">{a.url}</code>
                      <span className={`badge ${a.status === 'dangerous' ? 'badge-spam' : 'badge-ham'}`}>
                        {a.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="mt-2">Risk: <strong>{a.risk_percentage}%</strong></div>
                    <ul className="small mb-0 mt-1">
                      {a.risk_factors?.map((f, j) => <li key={j}>{f}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
            )}

            <div className="card card-hsds p-4 mb-4">
              <h5 className="mb-3">🧠 Explainable AI (XAI)</h5>
              <table className="table table-hsds table-sm">
                <thead>
                  <tr><th>Word</th><th>Impact</th><th>Contribution</th></tr>
                </thead>
                <tbody>
                  {(data.xai_data?.word_impact_table || []).map((w, i) => (
                    <tr key={i}>
                      <td>{w.word}</td>
                      <td className={`impact-${w.impact.toLowerCase()}`}>{w.impact}</td>
                      <td>{(w.contribution * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {chartData && (
                <div style={{ height: 250 }}>
                  <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
                </div>
              )}
            </div>

            <div className="card card-hsds p-4">
              <h5 className="mb-3">TextGuard Pipeline Steps</h5>
              {(data.hasadf_pipeline || []).map((step) => (
                <div key={step.step} className="pipeline-step">
                  <span className="step-num">{step.step}</span>
                  <div>
                    <strong>{step.name}</strong>
                    <div className="small text-muted">{step.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="col-lg-4">
            <div className="card card-hsds p-4 mb-4 text-center">
              <SecurityGauge score={data.security_score} />
              <p className="small text-muted mt-2">
                {(data.explanation?.reasons || []).slice(0, 3).join(' • ')}
              </p>
            </div>

            <div className="card card-hsds p-4 mb-4">
              <h6>Continuous Learning</h6>
              <p className="small text-muted">Was this prediction correct?</p>
              <div className="d-flex gap-2">
                <button className="btn btn-hsds btn-sm flex-fill" onClick={() => handleFeedback('correct')} disabled={!!feedbackSent}>
                  ✓ Correct
                </button>
                <button className="btn btn-outline-hsds btn-sm flex-fill" onClick={() => handleFeedback('wrong')} disabled={!!feedbackSent}>
                  ✗ Wrong
                </button>
              </div>
              {feedbackSent && <small className="text-success mt-2 d-block">Feedback recorded. Thank you!</small>}
            </div>

            <div className="card card-hsds p-4">
              <h6>Suspicious Words</h6>
              <div className="d-flex flex-wrap gap-1 mt-2">
                {(data.suspicious_words || []).map((w, i) => (
                  <span key={i} className="badge bg-danger">{w}</span>
                ))}
                {!data.suspicious_words?.length && <span className="text-muted small">None detected</span>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
