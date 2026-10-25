// Inline SVG illustrations recreating the mock motifs: document, magnifier, stop sign, clock, family, phone.
// Purely decorative unless a `label` is given; every text inside comes from i18n via props.
import { useId, type ReactNode } from 'react';

const RED = '#C62828';
const INK = '#111111';
const BAR = '#E4E4DF';

function useUid() { return useId().replace(/[^a-zA-Z0-9]/g, ''); }

function Bursts({ x, y, rot = 0, scale = 1, color = RED }: { x: number; y: number; rot?: number; scale?: number; color?: string }) {
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${scale})`} stroke={color} strokeWidth="5" strokeLinecap="round">
      <path d="M0 0 L8 -26" /><path d="M18 8 L40 -10" /><path d="M24 30 L50 26" />
    </g>
  );
}

function Briefcase({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} fill="none" stroke={INK} strokeWidth="3.2" strokeLinejoin="round" strokeLinecap="round">
      <rect x="0" y="10" width="44" height="32" rx="5" /><path d="M14 10 V4 Q14 0 18 0 H26 Q30 0 30 4 V10" /><path d="M0 22 H44" /><path d="M18 22 V27 H26 V22" />
    </g>
  );
}
function Building({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`} fill="none" stroke={INK} strokeWidth="2.6" strokeLinejoin="round">
      <path d="M4 34 V6 Q4 4 6 4 H10 V0 H16 V4 H20 Q22 4 22 6 V34 Z" />
      <path d="M9 11 h2 M15 11 h2 M9 18 h2 M15 18 h2 M9 25 h2 M15 25 h2" strokeLinecap="round" />
    </g>
  );
}
function Plane({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y}) rotate(-35 16 16)`} fill="none" stroke={INK} strokeWidth="2.6" strokeLinejoin="round">
      <path d="M16 0 Q19 0 19 5 V12 L32 20 V24 L19 20 V27 L23 30 V33 L16 31 L9 33 V30 L13 27 V20 L0 24 V20 L13 12 V5 Q13 0 16 0 Z" />
    </g>
  );
}
function Signature({ x, y }: { x: number; y: number }) {
  return <path transform={`translate(${x} ${y})`} d="M0 40 C14 30 30 6 36 2 C40 -2 38 14 34 26 C32 32 42 18 48 18 C52 18 50 30 58 28 C66 26 74 24 90 26 M8 48 C30 44 60 42 96 44" fill="none" stroke="#3a3a36" strokeWidth="2.2" strokeLinecap="round" />;
}

function Page({ uid, children }: { uid: string; children?: ReactNode }) {
  return (
    <g>
      <path d="M42 20 H352 L440 108 V528 Q440 540 428 540 H42 Q30 540 30 528 V32 Q30 20 42 20 Z" fill={`url(#pg${uid})`} />
      <path d="M352 20 V96 Q352 108 364 108 H440 Z" fill={`url(#fd${uid})`} />
      {children}
    </g>
  );
}
function PageDefs({ uid }: { uid: string }) {
  return (
    <defs>
      <linearGradient id={`pg${uid}`} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="1" stopColor="#F2F2EE" /></linearGradient>
      <linearGradient id={`fd${uid}`} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset=".5" stopColor="#EDEDE8" /><stop offset="1" stopColor="#D9D9D3" /></linearGradient>
      <linearGradient id={`ring${uid}`} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#E64A45" /><stop offset=".55" stopColor="#C62828" /><stop offset="1" stopColor="#9F1D1D" /></linearGradient>
      <linearGradient id={`inkring${uid}`} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#4A4A46" /><stop offset=".55" stopColor="#151515" /><stop offset="1" stopColor="#000" /></linearGradient>
      <radialGradient id={`lens${uid}`} cx=".35" cy=".3" r=".8"><stop offset="0" stopColor="#FFFFFF" stopOpacity=".9" /><stop offset="1" stopColor="#F4F4F0" stopOpacity=".55" /></radialGradient>
    </defs>
  );
}

function Magnifier({ uid, cx, cy, r, tone = 'red', children }: { uid: string; cx: number; cy: number; r: number; tone?: 'red' | 'ink'; children?: ReactNode }) {
  const ring = tone === 'red' ? `url(#ring${uid})` : `url(#inkring${uid})`;
  const w = r * 0.2;
  const hx = cx + r * 0.72; const hy = cy + r * 0.72;
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={`url(#lens${uid})`} />
      {children}
      <g transform={`rotate(45 ${hx} ${hy})`}>
        <rect x={hx - w * 0.2} y={hy - w * 0.62} width={r * 0.95} height={w * 1.25} rx={w * 0.62} fill={ring} />
      </g>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={ring} strokeWidth={w} />
      <path d={`M${cx - r * 0.62} ${cy - r * 0.42} A ${r * 0.78} ${r * 0.78} 0 0 1 ${cx - r * 0.2} ${cy - r * 0.74}`} fill="none" stroke="#fff" strokeOpacity=".55" strokeWidth={w * 0.28} strokeLinecap="round" />
    </g>
  );
}

function Bars({ x, y, widths, gap = 25, h = 13 }: { x: number; y: number; widths: number[]; gap?: number; h?: number }) {
  return <g fill={BAR}>{widths.map((w, i) => <rect key={i} x={x} y={y + i * gap} width={w} height={h} rx={h / 2} />)}</g>;
}

/** The job-offer document used across home, submit, review and result screens. */
export function OfferDoc({
  title, demo, fieldLabel, fieldValue, callout, flagRow, magnifier = 'red', rotate = -5, bursts = true, className = '',
}: {
  title: string; demo: string; fieldLabel?: string; fieldValue?: string; callout?: string; flagRow?: string;
  magnifier?: 'red' | 'ink' | 'none'; rotate?: number; bursts?: boolean; className?: string;
}) {
  const uid = useUid();
  const lens = magnifier !== 'none' ? (fieldValue ? { cx: 320, cy: 300, r: 104 } : { cx: 330, cy: 330, r: 112 }) : null;
  return (
    <svg className={`illo ${className}`} viewBox="0 0 640 620" aria-hidden="true" focusable="false">
      <PageDefs uid={uid} />
      <g className="illo-shadow" transform={`rotate(${rotate} 235 280) translate(10 20)`}>
        <Page uid={uid}>
          <Briefcase x={66} y={62} />
          <text x="132" y="88" fontSize="30" fontWeight="760" style={{ fontStretch: '78%' }} fill={INK}>{title}</text>
          <text x="132" y="114" fontSize="17" fill="#8a8a84">{demo}</text>
          <Bars x={66} y={160} widths={[230, 150, 120]} />
          {flagRow ? (
            <g>
              <rect x="56" y="262" width="350" height="96" rx="14" fill="#FBE3E0" />
              <circle cx="96" cy="296" r="18" fill={RED} /><rect x="93.5" y="284" width="5" height="15" rx="2.5" fill="#fff" /><circle cx="96" cy="306" r="3" fill="#fff" />
              <text x="128" y="304" fontSize="24" fontWeight="600" fill={INK}>{flagRow}</text>
              <rect x="128" y="322" width="210" height="14" rx="7" fill="#F2B8B2" />
              <Bars x={66} y={384} widths={[300, 250, 140]} />
            </g>
          ) : (
            <g>
              <Bars x={66} y={262} widths={[120, 90, 130]} />
              <Building x={66} y={376} /><Bars x={112} y={384} widths={[130, 150]} gap={20} h={11} />
              <Plane x={64} y={446} /><Bars x={112} y={452} widths={[130, 100]} gap={20} h={11} />
            </g>
          )}
          <Signature x={300} y={462} />
        </Page>
      </g>
      {lens && (
        <Magnifier uid={uid} cx={lens.cx} cy={lens.cy} r={lens.r} tone={magnifier === 'ink' ? 'ink' : 'red'}>
          {fieldValue ? (
            <g>
              <text x={lens.cx - 70} y={lens.cy - 30} fontSize="16" fontWeight="600" letterSpacing="1" fill="#55554F">{fieldLabel}</text>
              <rect x={lens.cx - 74} y={lens.cy - 14} width="148" height="46" rx="10" fill="#FBE3E0" stroke="#F0B7B1" strokeWidth="1.5" />
              <text x={lens.cx} y={lens.cy + 16} fontSize="22" fontWeight="600" textAnchor="middle" fill={INK}>{fieldValue}</text>
              <rect x={lens.cx - 58} y={lens.cy + 48} width="72" height="11" rx="5.5" fill={BAR} />
            </g>
          ) : (
            <Bars x={lens.cx - 60} y={lens.cy - 30} widths={[120, 90]} gap={26} />
          )}
        </Magnifier>
      )}
      {callout && (
        <g className="pop">
          <g filter="drop-shadow(0 12px 18px rgba(198,40,40,.35))">
            <rect x="404" y="160" width="226" height="66" rx="33" fill={`url(#ring${uid})`} transform="rotate(4 517 193)" />
          </g>
          <g transform="rotate(4 517 193)">
            <circle cx="442" cy="193" r="19" fill="#fff" /><rect x="439.5" y="181" width="5" height="15" rx="2.5" fill={RED} /><circle cx="442" cy="203" r="3" fill={RED} />
            <text x="474" y="202" fontSize="25" fontWeight="650" fill="#fff" style={{ fontStretch: '86%' }}>{callout}</text>
          </g>
          {bursts && <Bursts x={586} y={128} rot={10} />}
        </g>
      )}
      {!callout && bursts && <Bursts x={520} y={70} rot={6} />}
    </svg>
  );
}

/** Mock 05: stacked documents, large red magnifier and a question card. */
export function VerifyIllo() {
  const uid = useUid();
  return (
    <svg className="illo" viewBox="0 0 620 620" aria-hidden="true" focusable="false">
      <PageDefs uid={uid} />
      <g className="illo-shadow">
        <g transform="rotate(10 420 300)"><rect x="330" y="150" width="250" height="330" rx="18" fill="#F1F1ED" /></g>
        <g transform="rotate(4 360 300)"><rect x="250" y="80" width="300" height="400" rx="18" fill="#F8F8F5" /></g>
        <g transform="rotate(-4 300 300) translate(130 40) scale(.8)"><Page uid={uid}><Bars x={70} y={300} widths={[260, 160, 140]} gap={30} /></Page></g>
      </g>
      <Magnifier uid={uid} cx={300} cy={240} r={130}><Bars x={230} y={190} widths={[150, 170, 140, 110]} gap={28} /></Magnifier>
      <g className="illo-shadow">
        <g transform="rotate(5 470 470)">
          <rect x="360" y="380" width="230" height="180" rx="22" fill="#fff" />
          <circle cx="475" cy="440" r="38" fill="#FBE3E0" />
          <text x="475" y="458" textAnchor="middle" fontSize="50" fontWeight="800" fill={RED}>?</text>
          <rect x="395" y="500" width="160" height="12" rx="6" fill={BAR} /><rect x="395" y="522" width="110" height="12" rx="6" fill={BAR} />
        </g>
      </g>
      <Bursts x={150} y={60} rot={-30} /><Bursts x={540} y={360} rot={20} scale={.9} />
    </svg>
  );
}

/** Mock 04: red stop octagon with exclamation. */
export function StopSign({ size = 220 }: { size?: number }) {
  const uid = useUid();
  const pts = Array.from({ length: 8 }, (_, i) => {
    const a = (Math.PI / 8) + (i * Math.PI) / 4;
    return `${120 + 96 * Math.cos(a)},${120 + 96 * Math.sin(a)}`;
  }).join(' ');
  return (
    <svg className="illo pop" viewBox="0 0 240 240" width={size} height={size} aria-hidden="true" focusable="false" style={{ width: size, maxWidth: '100%', overflow: 'visible' }}>
      <defs>
        <linearGradient id={`st${uid}`} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#E3423D" /><stop offset="1" stopColor="#B21F1F" /></linearGradient>
      </defs>
      <g stroke={RED} strokeWidth="5" strokeLinecap="round">
        <path d="M44 30 L62 48" /><path d="M196 30 L178 48" /><path d="M8 92 L34 98" /><path d="M232 92 L206 98" />
      </g>
      <polygon points={pts} fill="#fff" stroke="#fff" strokeWidth="18" strokeLinejoin="round" filter="drop-shadow(0 16px 26px rgba(198,40,40,.35))" />
      <polygon points={pts} fill={`url(#st${uid})`} stroke={`url(#st${uid})`} strokeWidth="4" strokeLinejoin="round" />
      <rect x="110" y="62" width="20" height="80" rx="10" fill="#fff" />
      <circle cx="120" cy="168" r="13" fill="#fff" />
    </svg>
  );
}

/** Ring clock used by safety setup (08) and traveller check-in (09). `fraction` = red arc share. */
export function ClockRing({ fraction, children, label }: { fraction: number; children?: ReactNode; label?: string }) {
  const uid = useUid();
  const f = Math.max(0, Math.min(1, fraction));
  const r = 180; const c = 200;
  const a = -Math.PI / 2 + f * 2 * Math.PI;
  const end = { x: c + r * Math.cos(a), y: c + r * Math.sin(a) };
  const large = f > 0.5 ? 1 : 0;
  return (
    <div className="clock" role={label ? 'img' : undefined} aria-label={label}>
      <svg className="illo" viewBox="0 0 400 400" aria-hidden="true" focusable="false">
        <defs>
          <radialGradient id={`face${uid}`} cx=".4" cy=".35" r=".75"><stop offset="0" stopColor="#FFFFFF" /><stop offset="1" stopColor="#F3F3EF" /></radialGradient>
        </defs>
        <circle cx={c} cy={c} r={r + 16} fill="#FBFBF8" filter="drop-shadow(0 24px 36px rgba(17,17,17,.12))" />
        <circle cx={c} cy={c} r={r} fill={`url(#face${uid})`} stroke="#ECECE7" strokeWidth="14" />
        {Array.from({ length: 12 }, (_, i) => {
          const t = (i * Math.PI) / 6;
          return <line key={i} x1={c + 140 * Math.sin(t)} y1={c - 140 * Math.cos(t)} x2={c + 156 * Math.sin(t)} y2={c - 156 * Math.cos(t)} stroke="#B5B5AE" strokeWidth="3.5" strokeLinecap="round" />;
        })}
        {f > 0.001 && (f >= 0.999
          ? <circle cx={c} cy={c} r={r} fill="none" stroke={RED} strokeWidth="14" />
          : <path d={`M${c} ${c - r} A ${r} ${r} 0 ${large} 1 ${end.x} ${end.y}`} fill="none" stroke={RED} strokeWidth="14" strokeLinecap="round" filter="drop-shadow(0 0 10px rgba(198,40,40,.35))" />)}
        {f > 0.001 && f < 0.999 && <circle cx={end.x} cy={end.y} r="17" fill="#fff" stroke="#EDEDE8" strokeWidth="2" filter="drop-shadow(0 4px 8px rgba(17,17,17,.2))" />}
      </svg>
      <div className="clock__center">{children}</div>
    </div>
  );
}

export function ClockGlyph({ size = 64 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <circle cx="32" cy="32" r="27" fill="none" stroke={RED} strokeWidth="5" />
      <path d="M30 16 V34 H42" fill="none" stroke={RED} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/** Home: line-drawn parent and child (outline style from mock 01). */
export function FamilyLine({ className = '' }: { className?: string }) {
  return (
    <svg className={`illo ${className}`} viewBox="0 0 220 200" aria-hidden="true" focusable="false">
      <g fill="none" stroke={INK} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <path d="M58 104 C40 100 34 78 38 60 C42 36 60 24 80 26 C102 28 114 46 112 68 C110 86 104 98 92 104" />
        <path d="M44 62 C60 64 82 52 92 36" />
        <path d="M66 108 C66 116 64 120 58 124 C34 130 18 146 16 196" />
        <path d="M86 108 C86 116 90 120 96 124" />
        <path d="M36 168 V196" />
        <circle cx="152" cy="118" r="24" fill="#F4F4F0" />
        <path d="M130 112 C138 102 160 98 174 110" />
        <path d="M120 196 C120 166 132 150 152 148 C172 150 184 166 186 196" fill="#F4F4F0" />
        <path d="M134 176 V196 M170 176 V196" />
      </g>
      <g stroke={RED} strokeWidth="4" strokeLinecap="round"><path d="M176 30 L184 12" /><path d="M188 44 L206 32" /></g>
    </svg>
  );
}

/** Check-in: flat two-person illustration (simple shapes, never photos). */
export function FamilyDuo({ className = '' }: { className?: string }) {
  return (
    <svg className={`illo ${className}`} viewBox="0 0 260 180" aria-hidden="true" focusable="false">
      <path d="M150 180 C150 140 166 122 190 120 C214 122 228 140 228 180 Z" fill="#CFCFCA" />
      <circle cx="190" cy="86" r="26" fill="#EBD3C3" />
      <path d="M164 82 C162 60 178 52 192 54 C208 54 220 64 214 80 C206 70 186 70 172 74 Z" fill="#1A1A1A" />
      <path d="M78 180 C78 138 96 118 124 116 C152 118 168 138 168 180 Z" fill={RED} />
      <path d="M92 104 C82 70 98 46 124 46 C152 46 166 70 156 104 C150 92 98 92 92 104 Z" fill="#1A1A1A" />
      <circle cx="124" cy="84" r="26" fill="#EBD3C3" />
      <path d="M100 80 C104 62 116 58 128 58 C140 58 150 66 150 80 C140 70 116 68 100 80 Z" fill="#1A1A1A" />
      <g stroke={RED} strokeWidth="4" strokeLinecap="round"><path d="M232 40 L244 28" /><path d="M236 58 L256 54" /><path d="M234 76 L250 86" /></g>
    </svg>
  );
}

function PersonGlyph({ x, y, s = 1, female = false }: { x: number; y: number; s?: number; female?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} fill="none" stroke={INK} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="0" cy="-20" r={female ? 10 : 12} />
      {female && <path d="M-12 -4 C-18 -16 -16 -34 0 -35 C16 -34 18 -16 12 -4" />}
      <path d="M-22 22 C-22 6 -12 -2 0 -2 C12 -2 22 6 22 22 Z" />
    </g>
  );
}

/** Mock 10: family phone with bell and two contact nodes. */
export function PhoneAlert() {
  return (
    <svg className="illo" viewBox="0 0 560 460" aria-hidden="true" focusable="false">
      <g className="illo-shadow">
        <rect x="60" y="40" width="200" height="390" rx="34" fill="#fff" stroke={INK} strokeWidth="6" />
        <rect x="132" y="56" width="56" height="12" rx="6" fill={INK} />
        <g opacity=".9">
          <rect x="72" y="80" width="176" height="338" rx="20" fill="#F1F1EC" />
          <path d="M72 150 C120 130 160 170 248 140" stroke="#fff" strokeWidth="14" fill="none" />
          <path d="M72 300 C110 260 170 290 248 250" stroke="#fff" strokeWidth="12" fill="none" />
          <path d="M150 80 C140 200 190 280 170 418" stroke="#fff" strokeWidth="10" fill="none" />
          <path d="M120 236 Q140 260 136 290 Q150 316 190 330" stroke="#B5B5AE" strokeWidth="3" strokeDasharray="6 7" fill="none" />
          <path d="M120 196 C108 196 100 206 100 216 C100 232 120 250 120 250 C120 250 140 232 140 216 C140 206 132 196 120 196 Z" fill="#fff" stroke={RED} strokeWidth="4" />
          <circle cx="120" cy="216" r="6" fill={RED} />
        </g>
      </g>
      <g className="pop">
        <circle cx="244" cy="76" r="44" fill={RED} filter="drop-shadow(0 10px 20px rgba(198,40,40,.45))" />
        <path d="M226 92 H262 C256 86 256 80 256 70 C256 60 250 54 244 54 C238 54 232 60 232 70 C232 80 232 86 226 92 Z" fill="#fff" />
        <circle cx="244" cy="98" r="5" fill="#fff" />
        <g stroke={RED} strokeWidth="5" strokeLinecap="round"><path d="M296 20 L300 0" /><path d="M308 38 L326 26" /><path d="M312 58 L332 54" /></g>
      </g>
      <path d="M262 236 H330 M330 236 C330 160 380 120 430 120 M330 236 C330 312 380 352 430 352" stroke={RED} strokeWidth="3" strokeDasharray="7 8" fill="none" />
      <circle cx="430" cy="120" r="7" fill={RED} /><circle cx="430" cy="352" r="7" fill={RED} />
      <circle cx="490" cy="120" r="58" fill="#FBE3E0" /><circle cx="490" cy="352" r="58" fill="#FBE3E0" />
      <PersonGlyph x={490} y={126} s={1.2} />
      <PersonGlyph x={490} y={358} s={1.2} female />
    </svg>
  );
}

/** Mock 11: report documents with brand mark and ZIP badge. */
export function HelpDocs() {
  const uid = useUid();
  return (
    <svg className="illo" viewBox="0 0 480 480" aria-hidden="true" focusable="false">
      <PageDefs uid={uid} />
      <circle cx="270" cy="210" r="200" fill="#FBE9E7" opacity=".75" />
      <g className="illo-shadow">
        <g transform="rotate(14 330 260)"><rect x="220" y="90" width="210" height="300" rx="16" fill="#C62828" /></g>
        <g transform="rotate(-8 200 250)"><rect x="80" y="80" width="250" height="320" rx="18" fill="#E2E2DD" /></g>
        <g transform="rotate(-4 220 240) translate(90 60) scale(.62)">
          <Page uid={uid}><Bars x={70} y={250} widths={[280, 240, 200, 260, 220, 120]} gap={36} h={14} /></Page>
        </g>
      </g>
      <g transform="translate(150 112) rotate(-4) scale(.62)">
        <path fill={RED} d="M18 8H92L80 30H42V44L82 68V112H8L20 90H58V76L18 52Z" /><path fill="#9F1D1D" d="M42 44L82 68L58 76L18 52Z" />
      </g>
      <g className="illo-shadow">
        <circle cx="390" cy="330" r="62" fill="#fff" />
        <path d="M372 300 H398 L412 314 V360 Q412 364 408 364 H372 Q368 364 368 360 V304 Q368 300 372 300 Z" fill="none" stroke={INK} strokeWidth="3.5" strokeLinejoin="round" />
        <path d="M390 304 V340" stroke={RED} strokeWidth="3" strokeDasharray="4 4" /><rect x="385" y="340" width="10" height="12" rx="3" fill="none" stroke={RED} strokeWidth="3" />
      </g>
    </svg>
  );
}

/** Mock 12: three report cards joined by a dashed red loop. */
export function PatternNodes() {
  const card = (x: number, y: number) => (
    <g className="illo-shadow">
      <rect x={x} y={y} width="170" height="180" rx="22" fill="#fff" />
      <g fill={RED}><circle cx={x + 36} cy={y + 44} r="5.5" /><circle cx={x + 54} cy={y + 44} r="5.5" /><circle cx={x + 72} cy={y + 44} r="5.5" /></g>
      <Bars x={x + 30} y={y + 78} widths={[106, 106, 60]} gap={28} h={13} />
    </g>
  );
  return (
    <svg className="illo" viewBox="0 0 600 480" aria-hidden="true" focusable="false">
      <circle cx="280" cy="250" r="230" fill="#FBE9E7" opacity=".55" />
      <path d="M196 230 C206 170 230 130 270 112 M378 112 C420 130 440 170 446 228 M424 370 C370 410 280 408 226 370" fill="none" stroke={RED} strokeWidth="2.5" strokeDasharray="6 7" />
      {card(196, 20)}{card(20, 220)}{card(380, 250)}
      <g fill={RED}><circle cx="270" cy="112" r="7" /><circle cx="196" cy="230" r="7" /><circle cx="446" cy="238" r="7" /><circle cx="226" cy="370" r="7" /></g>
    </svg>
  );
}

/** Mock 14: one hash at the centre linked to each district (data driven). */
export function HashGraph({ center, nodes, label }: { center: string; nodes: string[]; label: string }) {
  const n = Math.max(nodes.length, 1);
  const h = Math.max(420, n * 110);
  const cy = h / 2;
  return (
    <svg className="illo" viewBox={`0 0 640 ${h}`} role="img" aria-label={label} focusable="false">
      <circle cx="170" cy={cy} r="170" fill="none" stroke="#E9E9E4" /><circle cx="170" cy={cy} r="115" fill="none" stroke="#E9E9E4" />
      {nodes.map((name, i) => {
        const y = n === 1 ? cy : 60 + (i * (h - 120)) / (n - 1);
        const x = 380 + (Math.abs(y - cy) < 30 ? 60 : 0);
        return (
          <g key={name + i}>
            <path d={`M232 ${cy} C 300 ${cy} 300 ${y} ${x - 52} ${y}`} fill="none" stroke="#E57373" strokeWidth="2.5" />
            <circle cx={x - 52} cy={y} r="7" fill={RED} />
            <circle cx={x} cy={y} r="46" fill="#fff" stroke="#F3C3BE" strokeWidth="2" filter="drop-shadow(0 10px 18px rgba(198,40,40,.18))" />
            <Building x={x - 13} y={y - 18} />
            <circle cx={x + 36} cy={y - 36} r="17" fill="#fff" filter="drop-shadow(0 4px 8px rgba(17,17,17,.12))" />
            <path d={`M${x + 30} ${y - 45} h8 l5 5 v12 h-13 z`} fill="none" stroke={RED} strokeWidth="2" strokeLinejoin="round" />
            <text x={x + 62} y={y + 9} fontSize="26" fontWeight="760" style={{ fontStretch: '80%' }} fill={INK}>{name}</text>
          </g>
        );
      })}
      <circle cx="170" cy={cy} r="64" fill="#fff" stroke="#F3C3BE" strokeWidth="2" filter="drop-shadow(0 14px 28px rgba(198,40,40,.22))" />
      <PersonGlyph x={170} y={cy - 6} s={1} />
      <text x="170" y={cy + 40} textAnchor="middle" fontSize="15" className="mono" fill={INK}>{center}</text>
    </svg>
  );
}
