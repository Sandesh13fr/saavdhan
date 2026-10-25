import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import en from '../i18n/en.json';
import hi from '../i18n/hi.json';
import mr from '../i18n/mr.json';
import { ApiError } from './api';
import type { Lang } from './types';

const dict: Record<Lang, Record<string, string>> = { en, hi, mr };

// English fallbacks for the most visible keys so the UI is usable before copy lands.
const DEFAULTS: Record<string, string> = {
  'app.name': 'Saavdhan',
  'app.tagline': 'Check an overseas job offer before you pay or travel',
  'app.synthetic_badge': 'SYNTHETIC',
  'nav.check': 'Check', 'nav.verdict': 'Verdict', 'nav.safety': 'Safety plan', 'nav.family': 'Family',
  'nav.map': 'Map', 'nav.limits': 'Limits',
  'check.title': 'Check an offer',
  'check.paste_label': 'Paste the offer message',
  'check.upload_label': 'Or upload a PDF, text file or photo',
  'check.submit': 'Check this offer',
  'check.demo_title': 'Try a synthetic example',
  'check.demo_scam': 'Bangkok data-entry offer',
  'check.demo_near_miss': 'Dubai near-miss offer',
  'check.analyzing': 'Checking...',
  'verdict.title': 'Verdict',
  'verdict.STOP.title': 'STOP',
  'verdict.VERIFY_FIRST.title': 'VERIFY FIRST',
  'verdict.NO_RED_FLAGS_FOUND.title': 'NO RED FLAGS FOUND',
  'verdict.NO_RED_FLAGS_FOUND.body': 'No red flags found. Confirm with the Protector of Emigrants before paying anything.',
  'verdict.ra_list_date': 'Recruiting agent list dated {date}',
  'verdict.quote_label': 'Quoted from the offer',
  'verdict.heuristic_badge': 'heuristic',
  'verdict.rule_source': 'Rule source',
  'verdict.status.hit': 'Flag', 'verdict.status.clear': 'Clear', 'verdict.status.unknown': 'Unknown',
  'verdict.download_packet': 'Download evidence packet',
  'verdict.make_safety_plan': 'Make a safety plan',
  'verdict.facts_title': 'Facts we read from the offer',
  'verdict.method.llm': 'Read by an AI model; quotes checked against the text',
  'verdict.method.fallback': 'Read by simple pattern matching',
  'verdict.not_found': 'No offer loaded yet.',
  'severity.critical': 'Critical', 'severity.high': 'High', 'severity.medium': 'Medium', 'severity.low': 'Low', 'severity.info': 'Info',
  'safety.title': 'Family safety plan',
  'safety.checkin': 'Check in',
  'safety.save': 'Save plan',
  'safety.demo_advance': 'Skip ahead 24 hours (demo)',
  'safety.status.ok': 'On schedule', 'safety.status.due': 'Check-in due', 'safety.status.missed': 'Check-in missed',
  'family.title': "Family's phone",
  'family.simulated_badge': 'SIMULATED',
  'family.no_alerts': 'No alerts.',
  'map.title': 'Pattern map',
  'map.sign_in': 'Sign in',
  'limits.title': 'Limits and sources',
  'error.generic': 'Something went wrong. Please try again.',
  'error.network': 'Could not reach the service. Check your connection.',
  'error.unavailable': 'This feature is not available on the server yet.',
  'common.loading': 'Loading...',
};

interface Ctx {
  lang: Lang; setLang: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  err: (e: unknown) => string;
}
const I18n = createContext<Ctx>(null as unknown as Ctx);

function initial(): Lang {
  try { const v = localStorage.getItem('saavdhan.lang'); if (v === 'en' || v === 'hi' || v === 'mr') return v; } catch { /* storage blocked */ }
  return 'en';
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, set] = useState<Lang>(initial);
  const setLang = useCallback((l: Lang) => {
    set(l);
    try { localStorage.setItem('saavdhan.lang', l); } catch { /* storage blocked */ }
  }, []);
  const t = useCallback((key: string, vars?: Record<string, string | number>) => {
    let s = dict[lang][key] || dict.en[key] || DEFAULTS[key] || key;
    if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, String(v));
    return s;
  }, [lang]);
  // Maps a thrown error to user text; 405/501 mean the backend route is not built yet.
  const err = useCallback((e: unknown) => {
    if (e instanceof ApiError) {
      if (e.status === 0) return t('error.network');
      if ([405, 501].includes(e.status)) return t('error.unavailable');
      if (e.message) return e.message;
    }
    return t('error.generic');
  }, [t]);
  const value = useMemo(() => ({ lang, setLang, t, err }), [lang, setLang, t, err]);
  return <I18n.Provider value={value}>{children}</I18n.Provider>;
}

export const useI18n = () => useContext(I18n);
