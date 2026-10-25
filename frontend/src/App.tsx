import { FileSearch, Gavel, HeartHandshake, Info, Map as MapIcon, Smartphone } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ErrorNote, LanguageToggle, SyntheticBadge } from './components/small';
import { api, setCsrf } from './lib/api';
import { I18nProvider, useI18n } from './lib/i18n';
import type { CaseView } from './lib/types';
import CheckOffer from './screens/CheckOffer';
import FamilyPhone from './screens/FamilyPhone';
import Limits from './screens/Limits';
import PatternMap from './screens/PatternMap';
import SafetyPlan from './screens/SafetyPlan';
import Verdict from './screens/Verdict';

const TABS = [
  ['check', FileSearch], ['verdict', Gavel], ['safety', HeartHandshake],
  ['family', Smartphone], ['map', MapIcon], ['limits', Info],
] as const;
type Tab = (typeof TABS)[number][0];

function parseHash(): { tab: Tab; id: string } {
  const [tab, id] = location.hash.replace(/^#\/?/, '').split('/');
  return { tab: TABS.some(([k]) => k === tab) ? (tab as Tab) : 'check', id: id ?? '' };
}

function Shell() {
  const { t, err } = useI18n();
  const [route, setRoute] = useState(parseHash);
  const [view, setView] = useState<CaseView | null>(null);
  const [error, setError] = useState('');
  const [sessionReady, setSessionReady] = useState(false);
  const authStarted = useRef(false);

  useEffect(() => {
    if (authStarted.current) return;
    authStarted.current = true;
    api<{ authenticated?: boolean; csrf_token?: string }>('/auth/me').then((me) => {
      if (me.authenticated) setCsrf(me.csrf_token ?? '');
    }).catch((e) => setError(err(e))).finally(() => setSessionReady(true));
  }, [err]);

  useEffect(() => {
    const on = () => setRoute(parseHash());
    addEventListener('hashchange', on);
    return () => removeEventListener('hashchange', on);
  }, []);

  // Deep links and tab/focus refreshes share cancellation and request ordering.
  useEffect(() => {
    let active = true;
    let request = 0;
    const id = route.id || view?.id;
    if (route.id && view?.id !== route.id) { setView(null); setError(''); }
    const refresh = () => {
      if (!id) return;
      const latest = ++request;
      api<CaseView>(`/offers/${encodeURIComponent(id)}`).then((v) => {
        if (!active || latest !== request) return;
        setView((current) => current?.id === v.id && current.revision > v.revision ? current : v);
        setError('');
      }).catch((e) => { if (active && latest === request) setError(err(e)); });
    };
    if ((route.id && view?.id !== route.id) || route.tab === 'safety' || route.tab === 'family') refresh();
    addEventListener('focus', refresh);
    return () => { active = false; removeEventListener('focus', refresh); };
  }, [route.id, route.tab, err]);

  const go = useCallback((tab: Tab, id = view?.id ?? '') => { location.hash = `#/${tab}${id && tab !== 'check' && tab !== 'map' && tab !== 'limits' ? `/${id}` : ''}`; }, [view?.id]);
  const onCase = (v: CaseView) => { setView(v); setError(''); location.hash = `#/verdict/${v.id}`; };
  const onUpdate = (v: CaseView) => { if (v.id === parseHash().id) { setView(v); setError(''); } };

  const nav = (
    <nav aria-label="Main" className="nav">
      {TABS.map(([k, Icon]) => (
        <a key={k} href={`#/${k}${view && ['verdict', 'safety', 'family'].includes(k) ? `/${view.id}` : ''}`}
          aria-current={route.tab === k ? 'page' : undefined}>
          <Icon size={22} aria-hidden="true" /><span>{t(`nav.${k}`)}</span>
        </a>
      ))}
    </nav>
  );

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="top">
        <div className="top-in">
          <div className="brand"><strong>{t('app.name')}</strong><span>{t('app.tagline')}</span></div>
          {view?.demo && <SyntheticBadge />}
          <LanguageToggle />
        </div>
        <div className="nav-top">{nav}</div>
      </header>
      <main id="main" tabIndex={-1}>
        <ErrorNote message={error} />
        {!sessionReady ? <p>{t('common.loading')}</p> : <>
        {route.tab === 'check' && <CheckOffer onCase={onCase} />}
        {route.tab === 'verdict' && <Verdict view={view} onPlan={() => go('safety')} />}
        {route.tab === 'safety' && <SafetyPlan key={view?.id} view={view} onCase={onUpdate} />}
        {route.tab === 'family' && <FamilyPhone view={view} />}
        {route.tab === 'map' && <PatternMap />}
        {route.tab === 'limits' && <Limits />}
        </>}
      </main>
      <div className="nav-bottom">{nav}</div>
    </>
  );
}

export default function App() {
  return <I18nProvider><Shell /></I18nProvider>;
}
