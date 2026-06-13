import { useState, useEffect } from 'react'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

const LANG_OPTIONS = [
  { value: 'en-IN', label: 'English' },
  { value: 'hi-IN', label: 'Hindi' },
  { value: 'mr-IN', label: 'Marathi' },
]

export default function VoiceButton({
  onTranscript,
  getBaseText = () => '',
  disabled = false,
  size = 'md',
  showLangPicker = true,
  onListeningChange,
}) {
  const [language, setLanguage] = useState('en-IN')

  const { isListening, isSupported, error, toggle, stop } = useSpeechRecognition({
    language,
    onResult: onTranscript,
  })

  const handleClick = () => {
    if (disabled) return
    toggle(getBaseText())
  }

  useEffect(() => {
    onListeningChange?.(isListening)
  }, [isListening, onListeningChange])

  if (!isSupported) return null

  const btnClass = size === 'sm' ? 'voice-btn voice-btn-sm' : 'voice-btn'

  return (
    <div className="voice-control">
      {showLangPicker && (
        <select
          className="voice-lang-select"
          value={language}
          onChange={(e) => {
            if (isListening) stop()
            setLanguage(e.target.value)
          }}
          disabled={disabled || isListening}
          aria-label="Voice language"
        >
          {LANG_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      )}
      <button
        type="button"
        className={`${btnClass}${isListening ? ' listening' : ''}`}
        onClick={handleClick}
        disabled={disabled}
        title={isListening ? 'Stop listening' : 'Start voice input'}
        aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
      >
        <span className="voice-btn-icon" aria-hidden="true">
          {isListening ? '⏹' : '🎤'}
        </span>
        <span className="voice-btn-label">
          {isListening ? 'Listening...' : 'Voice'}
        </span>
      </button>
      {error && <small className="voice-error">{error}</small>}
    </div>
  )
}
