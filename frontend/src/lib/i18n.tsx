import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import en from '../i18n/en.json';
import hi from '../i18n/hi.json';
import mr from '../i18n/mr.json';
import { ApiError } from './api';
import type { Lang } from './types';

const dict: Record<Lang, Record<string, string>> = { en, hi, mr };



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
    let s = dict[lang][key] || dict.en[key] || key;
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
