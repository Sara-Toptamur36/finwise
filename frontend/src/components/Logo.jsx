import { useId } from 'react'

/**
 * FinWise logo simgesi — daire + yapraklar + bar grafik + ok
 */
export function LogoIcon({ size = 40 }) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '')
  const clipId = `fwc${uid}`

  return (
    <svg
      viewBox="0 0 60 65"
      width={size}
      height={Math.round(size * 65 / 60)}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="FinWise logo"
    >
      <defs>
        <clipPath id={clipId}>
          <circle cx="30" cy="42" r="20" />
        </clipPath>
      </defs>

      {/* Daire arka plan + koyu yeşil çerçeve */}
      <circle cx="30" cy="42" r="20" fill="white" stroke="#14532d" strokeWidth="3.2" />

      {/* Sol yaprak */}
      <path
        d="M30,22 C25,11 12,13 15,20.5 C17,26 25,24 30,22Z"
        fill="#14532d"
      />
      {/* Sağ yaprak */}
      <path
        d="M30,22 C35,11 48,13 45,20.5 C43,26 35,24 30,22Z"
        fill="#14532d"
      />

      {/* Bar grafikler + ok — daireye kırpılmış */}
      <g clipPath={`url(#${clipId})`}>
        {/* Bar 1 — kısa */}
        <rect x="14" y="47" width="7" height="17" rx="1" fill="#22c55e" />
        {/* Bar 2 — orta */}
        <rect x="23.5" y="37" width="7" height="27" rx="1" fill="#22c55e" />
        {/* Bar 3 — uzun */}
        <rect x="33" y="26" width="7" height="38" rx="1" fill="#22c55e" />

        {/* Ok gövdesi */}
        <line
          x1="11" y1="57" x2="45" y2="24"
          stroke="#22c55e" strokeWidth="2.6" strokeLinecap="round"
        />
        {/* Ok ucu */}
        <path
          d="M41,22.5 L45,24 L43.5,28.5"
          fill="none"
          stroke="#22c55e" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"
        />
      </g>
    </svg>
  )
}

/** İki renkli "FinWise" yazısı */
export function LogoText({ dark = false, className = 'text-lg font-black tracking-tight' }) {
  return (
    <span className={className}>
      <span style={{ color: dark ? '#ffffff' : '#14532d' }}>Fin</span>
      <span style={{ color: '#22c55e' }}>Wise</span>
    </span>
  )
}

/** Tam logo — simge + yazı + opsiyonel alt başlık */
export default function Logo({ size = 40, dark = false, showTagline = false }) {
  return (
    <div className="flex items-center gap-2.5">
      <LogoIcon size={size} />
      <div className="leading-tight">
        <LogoText dark={dark} className="text-xl font-black tracking-tight block" />
        {showTagline && (
          <span
            className="text-xs font-medium block"
            style={{ color: dark ? 'rgba(255,255,255,0.5)' : '#6b7280' }}
          >
            Akıllı Bütçe, Güçlü Gelecek
          </span>
        )}
      </div>
    </div>
  )
}
