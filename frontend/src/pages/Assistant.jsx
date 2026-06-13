import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { chatAPI } from '../api/client'
import VoiceButton from '../components/VoiceButton'
import { speakText, isSpeechSynthesisSupported } from '../hooks/useSpeechRecognition'

const SUGGESTIONS = [
  'Why is this SMS dangerous?',
  'What should I do if I clicked the link?',
  'How do phishing scams work?',
  'Is it safe to share OTP with bank staff?',
]

const WELCOME_LLM = "Hello! I'm your AI Security Assistant powered by Gemini/OpenAI. Ask me anything about SMS scams, phishing, fraud, or cybersecurity — I'll respond naturally like ChatGPT."
const WELCOME_FALLBACK = "Hello! I'm your SMS Security Assistant. Add a Gemini or OpenAI API key in backend/.env for full AI chat. I can still help with SMS security questions."

function formatReply(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/```[\s\S]*?```/g, (m) => m.replace(/```\w*\n?/g, ''))
}

export default function Assistant() {
  const { smsId } = useParams()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [llmStatus, setLlmStatus] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [autoSpeak, setAutoSpeak] = useState(false)
  const chatEnd = useRef(null)

  useEffect(() => {
    chatAPI.status().then(({ data }) => {
      setLlmStatus(data)
      setMessages([{
        role: 'assistant',
        text: data.llm_enabled ? WELCOME_LLM : WELCOME_FALLBACK,
        provider: data.llm_enabled ? data.provider : 'fallback',
      }])
    }).catch(() => {
      setMessages([{ role: 'assistant', text: WELCOME_FALLBACK, provider: 'fallback' }])
    })
  }, [])

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const buildHistory = (msgs) =>
    msgs
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({ role: m.role, content: m.text }))

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userText = text.trim()
    const historyBefore = buildHistory(messages)

    setMessages((prev) => [...prev, { role: 'user', text: userText }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await chatAPI.send(
        userText,
        smsId ? parseInt(smsId) : null,
        historyBefore,
      )
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: formatReply(data.reply),
          provider: data.provider || (data.llm_enabled ? 'llm' : 'fallback'),
        },
      ])
      if (autoSpeak) {
        speakText(formatReply(data.reply))
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Sorry, something went wrong. Please try again.', provider: 'error' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="mb-4">
              <h2 className="page-title mb-1">AI Security Assistant</h2>
              <p className="page-subtitle mb-0">
                {smsId ? 'Context-aware chat about your analyzed SMS.' : 'Ask anything about SMS security — type or use voice.'}
              </p>
            </div>

            {!llmStatus?.llm_enabled && (
              <div className="alert alert-warning small mb-3">
                <strong>Enable ChatGPT-like AI:</strong> Get a free Gemini key at{' '}
                <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer" className="alert-link">
                  Google AI Studio
                </a>
                , add <code>GEMINI_API_KEY=your_key</code> to <code>backend/.env</code>, then restart the backend.
              </div>
            )}

            <div className="card card-hsds">
              <div className="chat-messages">
                {messages.map((m, i) => (
                  <div key={i} className={`chat-bubble ${m.role}`}>
                    {m.text}
                    {m.role === 'assistant' && isSpeechSynthesisSupported() && (
                      <button
                        type="button"
                        className="speak-btn"
                        onClick={() => speakText(m.text)}
                        title="Listen to response"
                      >
                        🔊 Listen
                      </button>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="chat-bubble assistant">
                    <span className="typing-dots">Thinking</span>
                  </div>
                )}
                <div ref={chatEnd} />
              </div>

              <div className="p-3 border-top" style={{ borderColor: 'var(--hsds-border)' }}>
                <div className="d-flex flex-wrap gap-2 mb-3">
                  {SUGGESTIONS.map((s, i) => (
                    <button
                      key={i}
                      type="button"
                      className="btn btn-outline-hsds btn-sm"
                      onClick={() => sendMessage(s)}
                      disabled={loading}
                    >
                      {s}
                    </button>
                  ))}
                </div>
                <form
                  onSubmit={(e) => { e.preventDefault(); sendMessage(input) }}
                >
                  <div className="input-with-voice mb-2">
                    <input
                      className="form-control form-control-hsds"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Type or use voice to ask about SMS security..."
                      disabled={loading}
                      autoComplete="off"
                    />
                    <button type="submit" className="btn btn-hsds" disabled={loading || !input.trim()}>
                      {loading ? '...' : 'Send'}
                    </button>
                  </div>
                  <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <VoiceButton
                      onTranscript={setInput}
                      getBaseText={() => input}
                      disabled={loading}
                      size="sm"
                      onListeningChange={setIsListening}
                    />
                    {isListening && (
                      <small className="voice-listening-hint">🎙️ Listening — speak your question</small>
                    )}
                    {isSpeechSynthesisSupported() && (
                      <label className="small text-muted mb-0 ms-auto">
                        <input
                          type="checkbox"
                          className="form-check-input me-1"
                          checked={autoSpeak}
                          onChange={(e) => setAutoSpeak(e.target.checked)}
                        />
                        Auto-read AI replies aloud
                      </label>
                    )}
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
