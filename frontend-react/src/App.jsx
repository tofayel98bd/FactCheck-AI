import { useState, useRef, useEffect } from "react";
import {
  ShieldCheck,
  XCircle,
  AlertTriangle,
  Loader2,
  Sparkles,
  ImagePlus,
  Film,
  X,
  Link2,
  Radio,
  TrendingUp,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000/api/verify-fact";

const VERDICT_STYLES = {
  True: { label: "True", color: "#22E6A8", bg: "rgba(34,230,168,0.1)", Icon: ShieldCheck },
  False: { label: "False", color: "#FF4D6D", bg: "rgba(255,77,109,0.1)", Icon: XCircle },
  Misleading: { label: "Misleading", color: "#B678FF", bg: "rgba(182,120,255,0.1)", Icon: AlertTriangle },
};

const MOCK_RUMORS = [
  {
    bn: "৫জি টাওয়ার বসানোর কারণে এলাকার পাখি মারা যাচ্ছে — এমন দাবি ছড়িয়ে পড়েছে ভাইরাল পোস্টে",
    en: "Claim: 5G towers are killing local birds",
    verdict: "False",
  },
  {
    bn: "পুরনো একটি বন্যার ভিডিওকে সাম্প্রতিক ঘটনা বলে সামাজিক মাধ্যমে ছড়ানো হচ্ছে",
    en: "Old flood footage is being shared as a current event",
    verdict: "Misleading",
  },
  {
    bn: "একটি ব্যাংকিং অ্যাপে সাইন আপ করলেই ১০,০০০ টাকা বোনাস — ভাইরাল বার্তা",
    en: "Viral message promises a free bank-app sign-up bonus",
    verdict: "False",
  },
  {
    bn: "একজন তারকার নামে বসানো একটি বক্তব্যের স্ক্রিনশট ছড়িয়ে পড়েছে",
    en: "A fabricated quote screenshot is being shared",
    verdict: "False",
  },
  {
    bn: "নতুন আইনে ফ্রিল্যান্সারদের আয়কর দ্বিগুণ হবে বলে গুজব ছড়াচ্ছে",
    en: "Rumor claims a new law will double freelancer income tax",
    verdict: "Misleading",
  },
];

function TrustRing({ score = 0, color = "#4DA3FF" }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circumference);

  useEffect(() => {
    const clamped = Math.max(0, Math.min(100, Number(score) || 0));
    const id = requestAnimationFrame(() => {
      setOffset(circumference - (clamped / 100) * circumference);
    });
    return () => cancelAnimationFrame(id);
  }, [score, circumference]);

  return (
    <div className="relative h-32 w-32 shrink-0">
      <svg viewBox="0 0 120 120" className="h-32 w-32 -rotate-90">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: "stroke-dashoffset 1.1s cubic-bezier(0.16,1,0.3,1)",
            filter: `drop-shadow(0 0 6px ${color}aa)`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-3xl font-semibold tabular-nums" style={{ color }}>
          {score}
        </span>
        <span className="text-[11px] text-mist">Trust score</span>
      </div>
    </div>
  );
}

function UploadZone({ file, onFile, onClear }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = (files) => {
    const f = files?.[0];
    if (f) onFile(f);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={`group flex h-full min-h-[64px] cursor-pointer items-center gap-3 rounded-xl border border-dashed px-4 py-3 transition-colors ${
        dragging ? "border-electric bg-electric/5" : "border-white/12 hover:border-white/25"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*,video/*"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {file ? (
        <>
          {file.type.startsWith("image/") ? (
            <img src={URL.createObjectURL(file)} alt="" className="h-10 w-10 rounded-lg object-cover" />
          ) : (
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/5">
              <Film className="h-4 w-4 text-electric" />
            </span>
          )}
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm text-ink">{file.name}</p>
            <p className="text-xs text-mist">Attached — ready to verify</p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClear();
            }}
            className="rounded-full p-1.5 text-mist transition-colors hover:bg-white/5 hover:text-rose"
          >
            <X className="h-4 w-4" />
          </button>
        </>
      ) : (
        <>
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/5 text-mist transition-colors group-hover:text-electric">
            <ImagePlus className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm text-ink">Attach a screenshot, image or video</p>
            <p className="text-xs text-mist">Drag & drop, or click to browse</p>
          </div>
        </>
      )}
    </div>
  );
}

function ResultCard({ result }) {
  const v = VERDICT_STYLES[result.verdict] || VERDICT_STYLES.Misleading;
  const Icon = v.Icon;

  return (
    <div className="glass relative mt-6 animate-card-in overflow-hidden rounded-2xl p-6 sm:p-8">
      <div
        className="pointer-events-none absolute -top-24 right-0 h-56 w-56 rounded-full blur-3xl"
        style={{ background: v.color, opacity: 0.14 }}
      />

      <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center">
        <TrustRing score={result.trust_score ?? 0} color={v.color} />
        <div className="min-w-0 flex-1">
          <div
            className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
            style={{ color: v.color, background: v.bg, boxShadow: `0 0 16px ${v.color}33` }}
          >
            <Icon className="h-3.5 w-3.5" />
            {v.label}
          </div>
          <p className="mt-3 text-sm text-mist">Claim reviewed</p>
          <p className="mt-1 text-[15px] leading-relaxed text-ink/90">{result.claim}</p>
        </div>
      </div>

      <div className="relative mt-6 border-t border-white/8 pt-6">
        <p className="text-sm font-medium text-ink">Why</p>
        <p className="mt-2 text-[15px] leading-relaxed text-mist">{result.explanation}</p>
      </div>

      {Array.isArray(result.sources) && result.sources.length > 0 && (
        <div className="relative mt-6 border-t border-white/8 pt-6">
          <p className="text-sm font-medium text-ink">Sources</p>
          <div className="mt-3 flex flex-col gap-2">
            {result.sources.map((s, i) => (
              <a
                key={i}
                href={s.link}
                target="_blank"
                rel="noreferrer"
                className="group flex items-center gap-2 rounded-lg border border-white/8 bg-white/[0.02] px-3 py-2 text-sm text-ink/85 transition-colors hover:border-electric/40 hover:bg-electric/5"
              >
                <Link2 className="h-3.5 w-3.5 shrink-0 text-electric" />
                <span className="truncate">{s.title}</span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function RumorRadar() {
  const loopItems = [...MOCK_RUMORS, ...MOCK_RUMORS];

  return (
    <section className="relative mx-auto mt-20 max-w-3xl px-4 pb-24">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="h-4 w-4 text-violet" />
            <h2 className="font-display text-lg font-semibold text-ink">Top 5 live rumors</h2>
          </div>
          <p className="mt-1 font-bn text-sm text-mist">টপ ৫টি লাইভ গুজব</p>
        </div>
        <span className="flex shrink-0 items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-mist">
          <span className="h-1.5 w-1.5 rounded-full bg-violet animate-pulse-dot" />
          Live
        </span>
      </div>

      <div className="relative mt-5 overflow-hidden rounded-xl">
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-10 bg-gradient-to-r from-void to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-10 bg-gradient-to-l from-void to-transparent" />
        <div className="flex w-max animate-marquee gap-3 py-1">
          {loopItems.map((r, i) => (
            <div key={i} className="glass flex w-72 shrink-0 items-start gap-2.5 rounded-xl px-4 py-3">
              <TrendingUp className="mt-0.5 h-3.5 w-3.5 shrink-0 text-violet" />
              <p className="line-clamp-2 font-bn text-sm text-ink/85">{r.bn}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {MOCK_RUMORS.map((r, i) => (
          <div key={i} className="glass rounded-xl p-4">
            <div className="flex items-start justify-between gap-3">
              <p className="font-bn text-sm leading-relaxed text-ink/90">{r.bn}</p>
              <span
                className="shrink-0 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                style={{
                  color: r.verdict === "False" ? "#FF4D6D" : "#B678FF",
                  background: r.verdict === "False" ? "rgba(255,77,109,0.1)" : "rgba(182,120,255,0.1)",
                }}
              >
                {r.verdict}
              </span>
            </div>
            <p className="mt-2 text-xs text-mist">{r.en}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [claim, setClaim] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const canVerify = (claim.trim().length > 0 || file) && !loading;

  const handleVerify = async () => {
    if (!canVerify) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Image/video upload is UI-only for now — once the backend accepts
      // multipart data, switch this to a FormData body that includes `file`.
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim: claim.trim() }),
      });

      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Can't reach the fact-check server. Make sure the backend is running on port 8000."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-void font-sans text-ink">
      <div className="grid-texture pointer-events-none fixed inset-0 z-0" />

      <div className="relative z-10">
        <header className="mx-auto flex max-w-3xl items-center justify-between px-4 pt-8">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-electric to-violet">
              <ShieldCheck className="h-4 w-4 text-void" />
            </span>
            <div className="leading-tight">
              <p className="font-display text-[15px] font-semibold">FactCheck AI</p>
              <p className="text-[11px] text-mist">Fact verification</p>
            </div>
          </div>
          <span className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-mist">
            <span className="h-1.5 w-1.5 rounded-full bg-verdant animate-pulse-dot" />
            Live
          </span>
        </header>

        <main className="relative mx-auto max-w-3xl px-4 pt-16 sm:pt-20">
          <div className="aura relative text-center">
            <h1 className="relative font-display text-4xl font-semibold leading-tight text-ink sm:text-5xl">
              Verify before you believe
            </h1>
            <p className="relative mt-3 font-bn text-base text-mist">বিশ্বাস করার আগে যাচাই করুন</p>
          </div>

          <div className="glass relative mt-10 rounded-2xl p-4 sm:p-5">
            <textarea
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="Paste a claim, headline, or link…"
              rows={3}
              className="w-full resize-none bg-transparent px-2 py-2 text-[15px] text-ink placeholder:text-mist/70"
            />

            <div className="mt-2 grid gap-3 px-2 sm:grid-cols-[1fr_auto] sm:items-end">
              <UploadZone file={file} onFile={setFile} onClear={() => setFile(null)} />

              <button
                onClick={handleVerify}
                disabled={!canVerify}
                className="flex h-full items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-gradient-to-r from-electric to-violet px-6 py-3.5 font-display text-sm font-semibold text-void shadow-[0_0_24px_rgba(77,163,255,0.35)] transition-shadow hover:shadow-[0_0_36px_rgba(77,163,255,0.5)] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Verifying
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Verify truth
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="glass mt-6 flex items-start gap-3 rounded-xl border-l-2 border-l-rose px-4 py-3">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose" />
              <p className="text-sm text-ink/85">{error}</p>
            </div>
          )}

          {result && <ResultCard result={result} />}
        </main>

        <RumorRadar />
      </div>
    </div>
  );
}