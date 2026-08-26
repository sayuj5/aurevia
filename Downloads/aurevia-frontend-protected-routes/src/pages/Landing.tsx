import { Link } from 'react-router-dom'
import { HeartHandshake, ShieldCheck } from 'lucide-react'

export function Landing() {
  return (
    <div className="min-h-screen bg-[var(--color-paper)] flex flex-col">
      <header className="px-6 md:px-12 py-8">
        <div className="flex items-center gap-2">
          <img src="/aurevia-logo.png" alt="Aurevia" className="h-10 w-auto object-contain" />
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center">
        <p className="uppercase text-xs tracking-[0.2em] text-[var(--color-sage)] mb-4 font-medium">
          Dynamic Distress Monitoring
        </p>
        <h1 className="font-display text-4xl md:text-6xl font-medium max-w-3xl leading-[1.1] text-[var(--color-ink)]">
          A quieter way to be heard,
          <br />
          <span className="italic">and a faster way to be helped.</span>
        </h1>
        <p className="mt-6 max-w-xl text-[var(--color-ink-soft)] text-lg">
          Aurevia listens to what's said and how it's said — so support reaches
          the people who need it most, without delay.
        </p>

        <div className="mt-12 grid sm:grid-cols-2 gap-4 w-full max-w-xl">
          <Link
            to="/login"
            className="group rounded-2xl border border-[var(--color-border)] bg-white/60 p-6 text-left hover:border-[var(--color-sage)] hover:bg-white transition-all"
          >
            <HeartHandshake className="w-7 h-7 text-[var(--color-sage)] mb-3" />
            <h2 className="font-display text-xl mb-1">I'd like to share how I'm doing</h2>
            <p className="text-sm text-[var(--color-ink-soft)]">
              A private, guided check-in. Takes about 5 minutes.
            </p>
          </Link>

          <Link
            to="/login"
            className="group rounded-2xl border border-[var(--color-border)] bg-white/60 p-6 text-left hover:border-[var(--color-sage)] hover:bg-white transition-all"
          >
            <ShieldCheck className="w-7 h-7 text-[var(--color-ink)] mb-3" />
            <h2 className="font-display text-xl mb-1">I'm a counsellor or officer</h2>
            <p className="text-sm text-[var(--color-ink-soft)]">
              View the case queue and respond to active alerts.
            </p>
          </Link>
        </div>
      </main>

      <footer className="px-6 md:px-12 py-6 text-center text-xs text-[var(--color-ink-soft)]">
        Every response is encrypted and reviewed only by authorized support staff.
      </footer>
    </div>
  )
}
