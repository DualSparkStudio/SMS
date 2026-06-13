import { useState, useRef, useCallback, useEffect } from 'react'

const SpeechRecognition = typeof window !== 'undefined'
  ? (window.SpeechRecognition || window.webkitSpeechRecognition)
  : null

export function useSpeechRecognition({ onResult, language = 'en-IN' } = {}) {
  const [isListening, setIsListening] = useState(false)
  const [error, setError] = useState('')
  const recognitionRef = useRef(null)
  const isSupported = !!SpeechRecognition

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  const start = useCallback((baseText = '') => {
    if (!isSupported) {
      setError('Voice input is not supported in this browser. Please use Chrome or Edge.')
      return
    }

    setError('')
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = language
    recognitionRef.current = recognition

    recognition.onresult = (event) => {
      let transcript = ''
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      const prefix = baseText.trim() ? `${baseText.trim()} ` : ''
      onResult?.(`${prefix}${transcript}`.trim())
    }

    recognition.onerror = (event) => {
      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Allow microphone permission in your browser.')
      } else if (event.error === 'no-speech') {
        setError('No speech detected. Please try again.')
      } else if (event.error !== 'aborted') {
        setError('Voice recognition failed. Please try again.')
      }
      setIsListening(false)
    }

    recognition.onend = () => setIsListening(false)

    try {
      recognition.start()
      setIsListening(true)
    } catch {
      setError('Could not start voice recognition.')
      setIsListening(false)
    }
  }, [isSupported, language, onResult])

  const toggle = useCallback((baseText = '') => {
    if (isListening) stop()
    else start(baseText)
  }, [isListening, start, stop])

  useEffect(() => () => recognitionRef.current?.abort(), [])

  return { isListening, isSupported, error, start, stop, toggle }
}

export function speakText(text, language = 'en-IN') {
  if (!text || typeof window === 'undefined' || !window.speechSynthesis) return

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = language
  utterance.rate = 0.95
  window.speechSynthesis.speak(utterance)
}

export function isSpeechSynthesisSupported() {
  return typeof window !== 'undefined' && !!window.speechSynthesis
}
