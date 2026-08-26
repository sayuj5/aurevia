import { useState } from 'react'
import { ArrowLeft, ArrowRight, Mic, Type, Check } from 'lucide-react'
import { VoiceRecorder } from '../components/VoiceRecorder'
import { Button } from "@/components/ui/button";
// translation dictionary
const translations = {
  en: {
    title: "New Assessment",
    consentTitle: "Before we begin",
    consentBody: "This check-in is private. What you share is encrypted and seen only by your assigned support team — never made public. You can stop at any point, and skipping a question is always okay.",
    consentBtn: "I understand, continue",
    modeTitle: "How would you like to share?",
    modeBody: "Choose whichever feels easier right now.",
    modeSpeak: "Speak",
    modeWrite: "Write",
    btnBack: "Back",
    btnContinue: "Continue",
    progressLabel: "Assessment progress",
    questionLabel: "Question",
    urgentTitle: "Is there anything urgent you want us to know?",
    urgentBody: "You can skip this question if nothing needs immediate attention.",
    notePlaceholder: "Add a note, or leave this blank...",
    responsePlaceholder: "Write whatever feels important...",
    completeTitle: "Check-in complete",
    completeBody: "Thank you for sharing. Your support team can now review your check-in."
  },
  hi: {
    title: "नया मूल्यांकन",
    consentTitle: "शुरू करने से पहले",
    consentBody: "यह चेक-इन निजी है। आप जो साझा करते हैं वह एन्क्रिप्टेड है और केवल आपकी सहायता टीम द्वारा देखा जाता है — कभी सार्वजनिक नहीं किया जाता। आप किसी भी समय रुक सकते हैं, और किसी प्रश्न को छोड़ना हमेशा ठीक है।",
    consentBtn: "मैं समझता/समझती हूँ, जारी रखें",
    modeTitle: "आप कैसे साझा करना चाहेंगे?",
    modeBody: "जो भी अभी आसान लगे उसे चुनें।",
    modeSpeak: "बोलें",
    modeWrite: "लिखें",
    btnBack: "पीछे",
    btnContinue: "जारी रखें",
    progressLabel: "मूल्यांकन प्रगति",
    questionLabel: "प्रश्न",
    urgentTitle: "क्या कोई जरूरी बात है जो आप हमें बताना चाहते हैं?",
    urgentBody: "अगर किसी बात पर तुरंत ध्यान देने की जरूरत नहीं है, तो आप इस प्रश्न को छोड़ सकते हैं।",
    notePlaceholder: "नोट लिखें, या इसे खाली छोड़ दें...",
    responsePlaceholder: "जो महत्वपूर्ण लगे, वह लिखें...",
    completeTitle: "चेक-इन पूरा हुआ",
    completeBody: "साझा करने के लिए धन्यवाद। आपकी सहायता टीम अब आपके चेक-इन की समीक्षा कर सकती है।"
  },
  bn: {
    title: "নতুন মূল্যায়ন",
    consentTitle: "শুরু করার আগে",
    consentBody: "এই চেক-ইন ব্যক্তিগত। আপনি যা শেয়ার করেন তা এনক্রিপ্ট করা হয় এবং শুধুমাত্র আপনার নির্ধারিত সহায়তা দল দেখতে পায় — কখনো সর্বজনীন করা হয় না। আপনি যেকোনো সময় থামতে পারেন, এবং কোনো প্রশ্ন এড়িয়ে যাওয়া সবসময় ঠিক আছে।",
    consentBtn: "আমি বুঝতে পেরেছি, চালিয়ে যান",
    modeTitle: "আপনি কীভাবে শেয়ার করতে চান?",
    modeBody: "আপনার কাছে এখন যেটা সহজ মনে হয় সেটা বেছে নিন।",
    modeSpeak: "কথা বলুন",
    modeWrite: "লিখুন",
    btnBack: "পেছনে",
    btnContinue: "চালিয়ে যান",
    progressLabel: "মূল্যায়নের অগ্রগতি",
    questionLabel: "প্রশ্ন",
    urgentTitle: "এখন কি এমন কোনো জরুরি বিষয় আছে যা আপনি আমাদের জানাতে চান?",
    urgentBody: "তাৎক্ষণিক মনোযোগের প্রয়োজন না হলে আপনি এই প্রশ্নটি এড়িয়ে যেতে পারেন।",
    notePlaceholder: "একটি নোট লিখুন, অথবা খালি রাখুন...",
    responsePlaceholder: "যা গুরুত্বপূর্ণ মনে হয় লিখুন...",
    completeTitle: "চেক-ইন সম্পন্ন হয়েছে",
    completeBody: "শেয়ার করার জন্য ধন্যবাদ। আপনার সহায়তা দল এখন আপনার চেক-ইন পর্যালোচনা করতে পারে।"
  }
};

type Language = 'en' | 'hi' | 'bn';

type InputMode = 'voice' | 'text' | null

const CHECK_IN_QUESTIONS = [
  'How have you been feeling since we last spoke?',
  'Have you felt safe in your surroundings this week?',
  'Is there anything happening right now that feels urgent?',
]

const steps = ['consent', 'mode', 'checkin', 'incident', 'done'] as const
type Step = (typeof steps)[number]

export function Assessment() {
  const [lang, setLang] = useState<Language>('en');
  const t = translations[lang];
  const [step, setStep] = useState<Step>('consent')
  const [mode, setMode] = useState<InputMode>(null)
  const [answers, setAnswers] = useState<string[]>(['', '', ''])
  const [incidentNote, setIncidentNote] = useState('')
  const [questionIndex, setQuestionIndex] = useState(0)

  const idx = steps.indexOf(step)
  const goNext = () => setStep(steps[Math.min(idx + 1, steps.length - 1)])
  const goBack = () => {
    if (step === 'checkin' && questionIndex > 0) {
      setQuestionIndex((current) => current - 1)
      return
    }

    setStep(steps[Math.max(idx - 1, 0)])
  }

  const continueCheckIn = () => {
    if (questionIndex < CHECK_IN_QUESTIONS.length - 1) {
      setQuestionIndex((current) => current + 1)
      return
    }

    goNext()
  }
  

  return (
    <div className="min-h-screen bg-[var(--color-paper)] flex flex-col">
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-10 md:py-16">
        
        {/* ONE shared wrapper for both header and card to guarantee perfect alignment */}
        <div className="w-full max-w-xl">
          
          {/* Language Switcher Header */}
          <div className="flex justify-between items-center mb-5">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-sage)] mb-1">Aurevia / Check-in</p>
              <h1 className="font-display text-2xl md:text-3xl text-[var(--color-ink)]">{t.title}</h1>
            </div>
            
            <select 
              value={lang} 
              onChange={(e) => setLang(e.target.value as Language)}
              className="bg-white/60 border border-[var(--color-border)] text-[var(--color-ink)] text-xs rounded-full focus:border-[var(--color-sage)] block px-3 py-2 shadow-sm"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="bn">বাংলা (Bengali)</option>
            </select>
          </div>

          <div className="flex items-center gap-2 mb-5" aria-label={t.progressLabel}>
            {steps.map((item, index) => (
              <div key={item} className={`h-1 flex-1 rounded-full transition-colors ${index <= steps.indexOf(step) ? 'bg-[var(--color-sage)]' : 'bg-[var(--color-border)]'}`} />
            ))}
          </div>

          {/* The White Wizard Card */}
          <div className="bg-white/70 p-7 md:p-10 rounded-2xl shadow-sm border border-[var(--color-border)] backdrop-blur-sm">
            
            {step === 'consent' && (
            <div className="text-center">
              {/* Translated Consent Title */}
              <h1 className="font-display text-3xl md:text-4xl font-medium mb-4 text-gray-900">
                {t.consentTitle}
              </h1>
              
              {/* Translated Consent Body */}
              <p className="text-gray-600 mb-8 leading-relaxed">
                {t.consentBody}
              </p>
              
              {/* 👇 YOUR NEW SHADCN BUTTON GOES HERE 👇 */}
              <Button
                onClick={goNext}
                size="lg"
                className="gap-2 rounded-full bg-white/50 backdrop-blur-md border border-white/20 text-gray-900 hover:bg-white/60 transition-all shadow-sm"
              >
                {t.consentBtn} <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          )}

          {step === 'mode' && (
            <div>
              {/* Translated Mode Title & Body */}
              <h1 className="font-display text-3xl font-medium mb-2 text-center text-[var(--color-ink)]">
                {t.modeTitle}
              </h1>
              <p className="text-[var(--color-ink-soft)] text-center mb-8">
                {t.modeBody}
              </p>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setMode('voice')}
                  className={`rounded-2xl border-2 p-6 flex flex-col items-center gap-3 transition-all ${
                    mode === 'voice' ? 'border-[var(--color-sage)] bg-white text-[var(--color-sage)]' : 'border-[var(--color-border)] bg-white/40 text-[var(--color-ink-soft)] hover:border-[var(--color-sage-light)]'
                  }`}
                >
                  <Mic className="w-6 h-6" />
                  {/* Translated Speak option */}
                  <span className="font-medium text-sm">{t.modeSpeak}</span>
                </button>
                <button
                  onClick={() => setMode('text')}
                  className={`rounded-2xl border-2 p-6 flex flex-col items-center gap-3 transition-all ${
                    mode === 'text' ? 'border-[var(--color-sage)] bg-white text-[var(--color-sage)]' : 'border-[var(--color-border)] bg-white/40 text-[var(--color-ink-soft)] hover:border-[var(--color-sage-light)]'
                  }`}
                >
                  <Type className="w-6 h-6" />
                  {/* Translated Write option */}
                  <span className="font-medium text-sm">{t.modeWrite}</span>
                </button>
              </div>
              <div className="flex justify-between mt-10">
                <button onClick={goBack} className="text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] font-medium">
                  {/* Translated Back Button */}
                  {t.btnBack}
                </button>
                <button
                  disabled={!mode}
                  onClick={goNext}
                  className="inline-flex items-center gap-2 bg-[var(--color-ink)] text-white px-6 py-3 rounded-full disabled:opacity-30 disabled:cursor-not-allowed hover:bg-[var(--color-sage)] transition-colors"
                >
                  {/* Translated Continue Button */}
                  {t.btnContinue} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 'checkin' && (
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.14em] text-[var(--color-sage)] mb-3">
                {t.questionLabel} {questionIndex + 1} / {CHECK_IN_QUESTIONS.length}
              </p>
              <h1 className="font-display text-3xl font-medium mb-8 text-[var(--color-ink)]">
                {CHECK_IN_QUESTIONS[questionIndex]}
              </h1>

              {mode === 'voice' ? (
                <VoiceRecorder
                  key={questionIndex}
                  onRecordingChange={(recording) => {
                    setAnswers((current) => {
                      const next = [...current]
                      next[questionIndex] = recording ? 'Voice response recorded' : ''
                      return next
                    })
                  }}
                />
              ) : (
                <textarea
                  value={answers[questionIndex]}
                  onChange={(event) => {
                    setAnswers((current) => {
                      const next = [...current]
                      next[questionIndex] = event.target.value
                      return next
                    })
                  }}
                  placeholder={t.responsePlaceholder}
                  className="w-full min-h-40 resize-y rounded-2xl border border-[var(--color-border)] bg-white/60 p-4 text-[var(--color-ink)] outline-none transition focus:border-[var(--color-sage)] focus:ring-2 focus:ring-[var(--color-sage)]/20"
                />
              )}

              <div className="flex justify-between mt-10">
                <button onClick={goBack} className="inline-flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] font-medium">
                  <ArrowLeft className="w-4 h-4" /> {t.btnBack}
                </button>
                <button
                  onClick={continueCheckIn}
                  className="inline-flex items-center gap-2 bg-[var(--color-ink)] text-white px-6 py-3 rounded-full hover:bg-[var(--color-sage)] transition-colors"
                >
                  {t.btnContinue} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 'incident' && (
            <div>
              <h1 className="font-display text-3xl font-medium mb-3 text-[var(--color-ink)]">
                {t.urgentTitle}
              </h1>
              <p className="text-[var(--color-ink-soft)] mb-8">
                {t.urgentBody}
              </p>
              <textarea
                value={incidentNote}
                onChange={(event) => setIncidentNote(event.target.value)}
                placeholder={t.notePlaceholder}
                className="w-full min-h-40 resize-y rounded-2xl border border-[var(--color-border)] bg-white/60 p-4 text-[var(--color-ink)] outline-none transition focus:border-[var(--color-sage)] focus:ring-2 focus:ring-[var(--color-sage)]/20"
              />
              <div className="flex justify-between mt-10">
                <button onClick={goBack} className="inline-flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] font-medium">
                  <ArrowLeft className="w-4 h-4" /> {t.btnBack}
                </button>
                <button
                  onClick={goNext}
                  className="inline-flex items-center gap-2 bg-[var(--color-ink)] text-white px-6 py-3 rounded-full hover:bg-[var(--color-sage)] transition-colors"
                >
                  {t.btnContinue} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 'done' && (
            <div className="text-center">
              <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--color-sage)]/15 text-[var(--color-sage)]">
                <Check className="w-7 h-7" />
              </div>
              <h1 className="font-display text-3xl font-medium mb-3 text-[var(--color-ink)]">
                {t.completeTitle}
              </h1>
              <p className="text-[var(--color-ink-soft)] leading-relaxed">
                {t.completeBody}
              </p>
            </div>
          )}
          </div>
        </div>
      </main>
    </div>
  );
}
