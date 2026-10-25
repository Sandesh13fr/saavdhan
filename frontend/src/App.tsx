import { BellRing, LifeBuoy, ScanSearch } from 'lucide-react';
import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { Logo } from './components/Brand';
import { DemoMenu, ErrorNote, LangSelect } from './components/ui';
import { api, setCsrf } from './lib/api';
import { I18nProvider, useI18n } from './lib/i18n';
import type { CaseView } from './lib/types';
import CheckIn from './screens/CheckIn';
import Evidence from './screens/Evidence';
import FamilyAlert from './screens/FamilyAlert';
import Help from './screens/Help';
import Home from './screens/Home';
import Login from './screens/Login';
import Result from './screens/Result';
import Review from './screens/Review';
import SafetySetup from './screens/SafetySetup';
import Submit from './screens/Submit';
import { Loading } from './screens/common';

// Leaflet and the boundary file load only for signed-in institution screens.
const PatternMapScreen = lazy(() => import('./screens/PatternMap'));
const PatternDetail = lazy(() => import('./screens/PatternDetail'));

import { go, parseHash, type Screen } from './lib/route';

const CASE_SCREENS: Screen[] = ['review', 'result', 'evidence', 'plan', 'checkin', 'family', 'help'];

function Shell() {
  const { t, err, lang } = useI18n();
  const [route, setRoute] = useState(parseHash);
  const [view, setView] = useState<CaseView | null>(null);
  const [error, setError] = useState('');
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const started = useRef(false);

  useEffect(() => { document.documentElement.lang = lang; }, [lang]);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    api<{ authenticated?: boolean; csrf_token?: string }>('/auth/me').then((me) => {
      if (me.authenticated) setCsrf(me.csrf_token ?? '');
      setAuthed(!!me.authenticated);
    }).catch(() => setAuthed(false));
  }, []);

  useEffect(() => {
    const on = () => { setRoute(parseHash()); window.scrollTo(0, 0); (document.getElementById('main') as HTMLElement | null)?.focus({ preventScroll: true }); };
    addEventListener('hashchange', on);
    return () => removeEventListener('hashchange', on);
  }, []);

  // Deep links and focus refreshes share cancellation and request ordering.
  const caseId = CASE_SCREENS.includes(route.screen) ? route.arg : '';
  useEffect(() => {
    let active = true;
    let request = 0;
    const id = caseId;
    if (!id) return;
    if (view?.id !== id) { setView(null); setError(''); }
    const refresh = () => {
      const latest = ++request;
      api<CaseView>(`/offers/${encodeURIComponent(id)}`).then((v) => {
        if (!active || latest !== request) return;
        setView((cur) => cur?.id === v.id && cur.revision > v.revision ? cur : v);
        setError('');
      }).catch((e) => { if (active && latest === request) setError(err(e)); });
    };
    if (view?.id !== id || route.screen === 'checkin' || route.screen === 'family') refresh();
    addEventListener('focus', refresh);
    return () => { active = false; removeEventListener('focus', refresh); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId, route.screen, err]);

  const onUpdate = useCallback((v: CaseView) => { setView(v); setError(''); }, []);

  // Create a case (upload/paste or demo), analyze it with Python rules, then open the review step.
  const startCase = useCallback(async (create: () => Promise<CaseView>) => {
    setBusy(true); setError('');
    try {
      const created = await create();
      const analyzed = await api<CaseView>(`/offers/${created.id}/analyze`, {});
      setView(analyzed);
      go('review', analyzed.id);
      return true;
    } catch (e) { setError(err(e)); return false; } finally { setBusy(false); }
  }, [err]);
  const startDemo = useCallback((name: string) => {
    if (route.screen !== 'check') go('check');
    void startCase(() => api<CaseView>(`/demo/offers/${name}`, {}));
  }, [startCase, route.screen]);

  const s = route.screen;
  const active = (['home', 'check', 'review', 'result', 'evidence'] as Screen[]).includes(s) ? 'check'
    : (['plan', 'checkin', 'family'] as Screen[]).includes(s) ? 'checkins' : s === 'help' ? 'help' : '';
  const id = view?.id ?? '';
  const checkinsHref = id ? `#/${view?.safety ? 'checkin' : 'plan'}/${id}` : '#/checkin';
  const navItems = [
    ['check', '#/', t('nav2.check'), ScanSearch],
    ['checkins', checkinsHref, t('nav2.checkins'), BellRing],
    ['help', id ? `#/help/${id}` : '#/help', t('nav2.help'), LifeBuoy],
  ] as const;
  const caseView = view && view.id === caseId ? view : null;

  return (
    <>
      <a className="skip" href="#main" onClick={(e) => { e.preventDefault(); document.getElementById('main')?.focus(); }}>{t('ui.skip')}</a>
      <header className="site-head">
        <div className="site-head__in">
          <Logo label={t('ui.home_label')} />
          <nav className="top-nav" aria-label={t('ui.main_nav')}>
            {navItems.map(([k, href, label]) => <a key={k} href={href} aria-current={active === k ? 'page' : undefined}>{label}</a>)}
          </nav>
          <span className="head-sep" aria-hidden="true" />
          <LangSelect />
          <DemoMenu onDemo={startDemo} busy={busy} />
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        {error && <div className="page" style={{ paddingBottom: 0 }}><ErrorNote message={error} /></div>}
        {s === 'home' && <Home />}
        {s === 'check' && <Submit busy={busy} onSubmit={(fd) => startCase(() => api<CaseView>('/offers', fd))} onDemo={startDemo} />}
        {s === 'review' && <Review view={caseView} />}
        {s === 'result' && <Result view={caseView} />}
        {s === 'evidence' && <Evidence view={caseView} />}
        {s === 'plan' && <SafetySetup key={caseView?.id ?? 'none'} view={caseView} caseId={caseId} onCase={onUpdate} />}
        {s === 'checkin' && <CheckIn view={caseView} caseId={caseId} onCase={onUpdate} />}
        {s === 'family' && <FamilyAlert view={caseView} caseId={caseId} />}
        {s === 'help' && <Help view={caseView} />}
        {s === 'login' && <Login authed={!!authed} onAuthed={() => { setAuthed(true); go('map'); }} />}
        <Suspense fallback={<Loading />}>
          {s === 'map' && <PatternMapScreen authed={authed} onSignedOut={() => setAuthed(false)} />}
          {s === 'pattern' && <PatternDetail authed={authed} hash={route.arg} />}
        </Suspense>
      </main>
      <footer className="site-foot">
        <span>{t('ui.footer')}</span>
        <a href={authed ? '#/map' : '#/login'}>{t('ui.institution_link')}</a>
      </footer>
      <nav className="tabbar" aria-label={t('ui.main_nav_mobile')}>
        {navItems.map(([k, href, label, Icon]) => (
          <a key={k} href={href} aria-current={active === k ? 'page' : undefined}><Icon size={24} aria-hidden="true" />{label}</a>
        ))}
      </nav>
    </>
  );
}

export default function App() {
  return <I18nProvider><Shell /></I18nProvider>;
}
