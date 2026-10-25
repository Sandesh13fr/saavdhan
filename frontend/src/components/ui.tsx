import { AlertCircle, ArrowRight, Check, ChevronDown, FileText, Info, Plane } from 'lucide-react';
import { Fragment, useEffect, useId, useRef, useState, type ReactNode } from 'react';
import { useI18n } from '../lib/i18n';
import type { FieldValue, Lang } from '../lib/types';

/** Heavy condensed headline; terminal punctuation of each sentence turns Alert red (brand rule). */
export function Headline({ text, as: Tag = 'h1', size = '', id, className = '' }: { text: string; as?: 'h1' | 'h2'; size?: '' | 'xl' | 'md' | 'sm'; id?: string; className?: string }) {
  const parts = text.split(/(?<=[.?!।])\s+/).filter(Boolean);
  return (
    <Tag id={id} className={`headline ${size ? `headline--${size}` : ''} ${className}`}>
      {parts.map((p, i) => {
        const m = p.match(/^(.*?)([.?!।]+)$/s);
        return (
          <Fragment key={i}>
            <span className={parts.length > 1 ? 'line' : undefined}>{m ? <>{m[1]}<span className="dot">{m[2]}</span></> : p}</span>
            {i < parts.length - 1 && ' '}
          </Fragment>
        );
      })}
    </Tag>
  );
}

type PillProps = { children: ReactNode; tone?: 'ink' | 'red'; wide?: boolean; small?: boolean; busy?: boolean };
export function PillButton({ children, tone = 'ink', wide, small, busy, ...rest }: PillProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button {...rest} className={`pill ${tone === 'red' ? 'pill--red' : ''} ${wide ? 'pill--wide' : ''} ${small ? 'pill--sm' : ''}`} aria-busy={busy || undefined}>
      <span>{children}</span>
      <span className="pill__arrow" aria-hidden="true">{busy ? <span className="spinner spinner--dark" /> : <ArrowRight size={small ? 20 : 24} strokeWidth={2.2} />}</span>
    </button>
  );
}
export function PillLink({ children, tone = 'ink', wide, small, ...rest }: PillProps & React.AnchorHTMLAttributes<HTMLAnchorElement>) {
  return (
    <a {...rest} className={`pill ${tone === 'red' ? 'pill--red' : ''} ${wide ? 'pill--wide' : ''} ${small ? 'pill--sm' : ''}`}>
      <span>{children}</span>
      <span className="pill__arrow" aria-hidden="true"><ArrowRight size={small ? 20 : 24} strokeWidth={2.2} /></span>
    </a>
  );
}

export function DemoChip({ label }: { label?: string }) {
  const { t } = useI18n();
  return <span className="chip"><span className="ico-badge" style={{ background: 'transparent', color: '#3f3f3b' }}><FileText size={18} aria-hidden="true" /></span>{label ?? t('ui.demo_data')}</span>;
}
export function AlertChip({ children, icon = 'alert' }: { children: ReactNode; icon?: 'alert' | 'info' }) {
  return (
    <span className="chip chip--red">
      <span className="ico-badge">{icon === 'info' ? <Info size={16} strokeWidth={2.6} aria-hidden="true" /> : <AlertCircle size={16} strokeWidth={2.6} aria-hidden="true" />}</span>
      {children}
    </span>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return message ? <p className="error-note" role="alert"><AlertCircle size={20} aria-hidden="true" /> <span>{message}</span></p> : null;
}

/** Add / Review / Result stepper from mocks 02-03. */
export function Stepper({ step }: { step: 1 | 2 | 3 }) {
  const { t } = useI18n();
  const items = [t('steps.add'), t('steps.review'), t('steps.result')];
  return (
    <nav className="stepper" aria-label={t('steps.label')}>
      <ol>
        {items.map((label, i) => {
          const n = i + 1;
          const state = n < step ? 'done' : n === step ? 'current' : 'todo';
          return (
            <li key={label} className={`stepper__item is-${state}`} aria-current={state === 'current' ? 'step' : undefined}>
              <span className="stepper__dot">{state === 'done' ? <Check size={18} strokeWidth={3} aria-hidden="true" /> : n}</span>
              <span className="stepper__label">{label}{state === 'done' && <span className="sr-only"> ({t('steps.done')})</span>}</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export function QuoteBlock({ field }: { field: FieldValue }) {
  const { t } = useI18n();
  if (!field.quote) return null;
  return (
    <figure className="quote">
      <blockquote lang="und">{field.quote}</blockquote>
      <figcaption>{t('verdict.source_label')}: {field.source_ref ?? '—'}</figcaption>
    </figure>
  );
}

/** Small popover menu closed by Escape and outside click; trigger keeps aria-expanded. */
export function useMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const id = useId();
  useEffect(() => {
    if (!open) return;
    const down = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) setOpen(false); };
    const key = (e: KeyboardEvent) => { if (e.key === 'Escape') { setOpen(false); (ref.current?.querySelector('[aria-expanded]') as HTMLElement | null)?.focus(); } };
    document.addEventListener('mousedown', down); document.addEventListener('keydown', key);
    return () => { document.removeEventListener('mousedown', down); document.removeEventListener('keydown', key); };
  }, [open]);
  return { open, setOpen, ref, id };
}

export const DEMOS = [['bangkok-data-entry', 'check.demo_scam', 'demo.bangkok_hint'], ['dubai-near-miss', 'check.demo_near_miss', 'demo.dubai_hint']] as const;

export function DemoMenu({ onDemo, busy, trigger = 'button', align = 'right' }: { onDemo: (name: string) => void; busy?: boolean; trigger?: 'button' | 'link'; align?: 'left' | 'right' }) {
  const { t } = useI18n();
  const m = useMenu();
  return (
    <div className="demo-menu" ref={m.ref}>
      <button type="button" className={trigger === 'button' ? 'btn-demo' : 'link-btn'} aria-expanded={m.open} aria-controls={m.id} onClick={() => m.setOpen(!m.open)} disabled={busy}>
        {trigger === 'button' ? t('ui.demo') : t('submit.try_demo')}
      </button>
      {m.open && (
        <div className={`menu-pop ${align === 'left' ? 'menu-pop--left' : ''}`} id={m.id} role="group" aria-label={t('check.demo_title')}>
          <p className="menu-pop__label">{t('check.demo_title')} <span className="chip chip--sm">{t('ui.demo_data')}</span></p>
          {DEMOS.map(([name, key, hint]) => (
            <button key={name} type="button" onClick={() => { m.setOpen(false); onDemo(name); }}>
              <span className="ico-circle ico-circle--red" aria-hidden="true"><Plane size={18} /></span>
              <span>{t(key)}<small>{t(hint)}</small></span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

const LANGS: [Lang, string][] = [['en', 'EN'], ['hi', 'हिंदी'], ['mr', 'मराठी']];
export function LangSelect() {
  const { lang, setLang, t } = useI18n();
  return (
    <label className="lang-select">
      <span className="sr-only">{t('ui.language')}</span>
      <select value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
        {LANGS.map(([code, label]) => <option key={code} value={code} lang={code}>{label}</option>)}
      </select>
      <ChevronDown size={18} aria-hidden="true" />
    </label>
  );
}

/** Accordion row used on results, evidence and pattern detail. */
export function Disclosure({ icon, title, sub, children, defaultOpen = false, className = '' }: { icon: ReactNode; title: ReactNode; sub?: ReactNode; children: ReactNode; defaultOpen?: boolean; className?: string }) {
  const [open, setOpen] = useState(defaultOpen);
  const id = useId();
  return (
    <div className={`row ${className}`}>
      <button type="button" className="row__head" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}>
        {icon}
        <span className="row__title"><strong>{title}</strong>{sub && <span>{sub}</span>}</span>
        <ChevronDown className="row__chev" size={24} aria-hidden="true" />
      </button>
      <div id={id} className="row__body" hidden={!open}>{children}</div>
    </div>
  );
}

export const fmtTime = (iso: string, lang: Lang) => {
  const d = new Date(iso);
  return isNaN(+d) ? iso : d.toLocaleTimeString(lang === 'en' ? 'en-IN' : `${lang}-IN`, { hour: 'numeric', minute: '2-digit' });
};
export const fmtDateTime = (iso: string, lang: Lang) => {
  const d = new Date(iso);
  return isNaN(+d) ? iso : d.toLocaleString(lang === 'en' ? 'en-IN' : `${lang}-IN`, { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' });
};
