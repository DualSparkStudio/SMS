import { useEffect, useState } from 'react'
import { analyticsAPI, mlAPI, campaignAPI } from '../api/client'

export default function Admin() {
  const [learning, setLearning] = useState(null)
  const [training, setTraining] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    analyticsAPI.learning().then(({ data }) => setLearning(data)).catch(() => {})
  }, [])

  const handleTrain = async (withFeedback) => {
    setTraining(true)
    setMessage('')
    try {
      const { data } = await mlAPI.train(withFeedback)
      setMessage(`Training complete! Best model: ${data.best_traditional?.model} (F1: ${data.best_traditional?.f1_score}%)`)
      analyticsAPI.learning().then(({ data: d }) => setLearning(d))
    } catch {
      setMessage('Training failed. Ensure you are logged in as admin.')
    } finally {
      setTraining(false)
    }
  }

  const handleDetectCampaigns = async () => {
    try {
      const { data } = await campaignAPI.detect()
      setMessage(`Detected ${data.detected} campaign(s).`)
    } catch {
      setMessage('Campaign detection failed. Admin access required.')
    }
  }

  return (
    <div className="page-container">
      <div className="container">
        <h2 className="mb-4">Admin Panel</h2>

        {message && <div className="alert alert-success">{message}</div>}

        <div className="row g-4">
          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h5 className="mb-3">Model Management</h5>
              <p className="text-muted small">Retrain ML models with latest data and user feedback.</p>
              <div className="d-flex gap-2">
                <button className="btn btn-hsds" onClick={() => handleTrain(false)} disabled={training}>
                  {training ? 'Training...' : 'Train Models'}
                </button>
                <button className="btn btn-outline-hsds" onClick={() => handleTrain(true)} disabled={training}>
                  Train with Feedback
                </button>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h5 className="mb-3">Campaign Detection</h5>
              <p className="text-muted small">Run clustering algorithm on spam messages.</p>
              <button className="btn btn-hsds" onClick={handleDetectCampaigns}>
                Detect Campaigns
              </button>
            </div>
          </div>

          <div className="col-12">
            <div className="card card-hsds p-4">
              <h5 className="mb-3">Continuous Learning Dashboard</h5>
              <div className="row g-3 mb-3">
                <div className="col-md-4">
                  <div className="stat-card">
                    <div className="stat-value">{learning?.total_feedback || 0}</div>
                    <div className="stat-label">Total Feedback</div>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="stat-card">
                    <div className="stat-value">{learning?.feedback_pending || 0}</div>
                    <div className="stat-label">Pending Corrections</div>
                  </div>
                </div>
              </div>

              {learning?.training_history?.length > 0 && (
                <table className="table table-hsds table-sm">
                  <thead>
                    <tr><th>Date</th><th>Model</th><th>Samples</th><th>Accuracy</th><th>F1</th></tr>
                  </thead>
                  <tbody>
                    {learning.training_history.map((log, i) => (
                      <tr key={i}>
                        <td>{new Date(log.trained_at).toLocaleDateString()}</td>
                        <td>{log.model}</td>
                        <td>{log.samples}</td>
                        <td>{log.accuracy}%</td>
                        <td>{log.f1_score}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
