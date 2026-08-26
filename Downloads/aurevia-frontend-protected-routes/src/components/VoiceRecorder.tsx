import { useState, useRef } from 'react'
import { Mic, Square, Play, Pause, Trash2 } from 'lucide-react'

export function VoiceRecorder({ onRecordingChange }: { onRecordingChange?: (blob: Blob | null) => void }) {
  const [status, setStatus] = useState<'idle' | 'recording' | 'recorded'>('idle')
  const [seconds, setSeconds] = useState(0)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioUrl(URL.createObjectURL(blob))
        onRecordingChange?.(blob)
        stream.getTracks().forEach((t) => t.stop())
      }

      recorder.start()
      mediaRecorderRef.current = recorder
      setStatus('recording')
      setSeconds(0)
      timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000)
    } catch {
      // Microphone unavailable or permission denied — the interface explains, doesn't apologize
      alert('Microphone access is needed to record. You can use the text option instead.')
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    if (timerRef.current) clearInterval(timerRef.current)
    setStatus('recorded')
  }

  const discard = () => {
    setAudioUrl(null)
    setStatus('idle')
    setSeconds(0)
    onRecordingChange?.(null)
  }

  const togglePlay = () => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  return (
    <div className="rounded-2xl border border-[var(--color-border)] bg-white/50 p-6 flex flex-col items-center gap-4">
      {status === 'idle' && (
        <>
          <button
            onClick={startRecording}
            className="w-20 h-20 rounded-full bg-[var(--color-sage)] hover:bg-[var(--color-ink)] transition-colors flex items-center justify-center shadow-sm"
            aria-label="Start voice recording"
          >
            <Mic className="w-8 h-8 text-white" />
          </button>
          <p className="text-sm text-[var(--color-ink-soft)] text-center">
            Tap to speak. Only you decide when to start and stop.
          </p>
        </>
      )}

      {status === 'recording' && (
        <>
          <button
            onClick={stopRecording}
            className="w-20 h-20 rounded-full bg-[var(--color-brick)] flex items-center justify-center shadow-sm relative"
            aria-label="Stop recording"
          >
            <span className="absolute inset-0 rounded-full bg-[var(--color-brick)] animate-ping opacity-30" />
            <Square className="w-7 h-7 text-white relative" fill="white" />
          </button>
          <p className="font-mono text-sm text-[var(--color-brick)]">{fmt(seconds)} · Recording</p>
        </>
      )}

      {status === 'recorded' && audioUrl && (
        <div className="w-full flex flex-col items-center gap-3">
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={() => setIsPlaying(false)}
            className="hidden"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="w-12 h-12 rounded-full bg-[var(--color-sage)] flex items-center justify-center"
              aria-label={isPlaying ? 'Pause playback' : 'Play recording'}
            >
              {isPlaying ? <Pause className="w-5 h-5 text-white" /> : <Play className="w-5 h-5 text-white ml-0.5" />}
            </button>
            <span className="font-mono text-sm text-[var(--color-ink-soft)]">{fmt(seconds)} recorded</span>
            <button
              onClick={discard}
              className="w-10 h-10 rounded-full hover:bg-[var(--color-paper-dim)] flex items-center justify-center transition-colors"
              aria-label="Discard recording and record again"
            >
              <Trash2 className="w-4 h-4 text-[var(--color-ink-soft)]" />
            </button>
          </div>
          <p className="text-xs text-[var(--color-ink-soft)]">You can re-record as many times as you need.</p>
        </div>
      )}
    </div>
  )
}
