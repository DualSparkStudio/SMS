import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { smsAPI } from '../api/client'
import VoiceButton from '../components/VoiceButton'

const ANALYSIS_STEPS = [
  'Detecting language...',
  'Scanning URLs for phishing...',
  'Checking fraud patterns...',
  'Running ML analysis...',
  'AI security verification...',
  'Calculating security score...',
]

const EXAMPLES = [
  { label: 'Spam (Lottery)', text: 'Congratulations! You won ₹50,000. Click here to claim your reward.' },
  { label: 'Spam (Banking)', text: 'URGENT: Your bank account will be blocked. Verify OTP immediately at http://sbi-secure-kyc.xyz' },
  { label: 'Ham (Normal)', text: 'Hey, are we still meeting for lunch tomorrow at 1pm?' },
  { label: 'Hindi Spam', text: 'आप इनाम जीत चुके हैं। अभी क्लिक करें और अपना पुरस्कार प्राप्त करें।' },
  { label: 'Marathi Spam', text: 'तुम्ही बक्षीस जिंकले आहे. त्वरित क्लिक करा आणि बक्षीस मिळवा.' },
]

export default function Detector() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [stepIndex, setStepIndex] = useState(0)
  const [error, setError] = useState('')
  const [isListening, setIsListening] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading) {
      setProgress(0)
      setStepIndex(0)
      return undefined
    }

    setProgress(8)
    setStepIndex(0)

    const stepTimer = setInterval(() => {
      setStepIndex((i) => (i + 1) % ANALYSIS_STEPS.length)
    }, 1400)

    const progressTimer = setInterval(() => {
      setProgress((p) => {
        if (p >= 96) return p
        if (p < 55) return p + 5
        if (p < 85) return p + 2
        return p + 0.4
      })
    }, 180)

    return () => {
      clearInterval(stepTimer)
      clearInterval(progressTimer)
    }
  }, [loading])

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!message.trim()) return
    setLoading(true)
    setError('')
    try {
      const { data } = await smsAPI.analyze(message)
      setProgress(100)
      navigate(`/results/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <h2 className="page-title text-center">SMS Security Analyzer</h2>
            <p className="page-subtitle text-center">
              Enter or speak an SMS message to analyze using TextGuard.
              Supports English, Hindi, and Marathi.
            </p>

            <div className="card card-hsds p-4">
              <form onSubmit={handleAnalyze}>
                <div className="mb-3">
                  <div className="label-with-voice">
                    <label className="form-label mb-0">SMS Message</label>
                    <VoiceButton
                      onTranscript={setMessage}
                      getBaseText={() => message}
                      disabled={loading}
                      onListeningChange={setIsListening}
                    />
                  </div>
                  <textarea
                    className="form-control form-control-hsds"
                    rows={5}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Paste, type, or use voice to dictate the SMS message..."
                    maxLength={5000}
                    disabled={loading}
                  />
                  <div className="d-flex justify-content-between align-items-center mt-1">
                    <small className="text-muted">{message.length}/5000 characters</small>
                    {isListening && (
                      <small className="voice-listening-hint">🎙️ Speak now — your words appear above</small>
                    )}
                  </div>
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                {loading && (
                  <div className="analysis-progress mb-3" aria-live="polite">
                    <div className="analysis-progress-header">
                      <span className="analysis-progress-step">{ANALYSIS_STEPS[stepIndex]}</span>
                      <span className="analysis-progress-pct">{Math.round(progress)}%</span>
                    </div>
                    <div className="analysis-progress-track">
                      <div
                        className="analysis-progress-bar"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <p className="analysis-progress-hint mb-0">
                      TextGuard is scanning your message for spam, phishing, and fraud...
                    </p>
                  </div>
                )}

                <button type="submit" className="btn btn-hsds w-100" disabled={loading || !message.trim()}>
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                      Analyzing...
                    </>
                  ) : (
                    '🔍 Analyze Message'
                  )}
                </button>
              </form>
            </div>

            <div className="mt-4">
              <h6 className="text-muted mb-3">Try an example:</h6>
              <div className="d-flex flex-wrap gap-2">
                {EXAMPLES.map((ex, i) => (
                  <button
                    key={i}
                    className="btn btn-outline-hsds btn-sm"
                    onClick={() => setMessage(ex.text)}
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
