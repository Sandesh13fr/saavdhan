import { useEffect, useState, type FormEvent } from 'react';
import { ErrorNote, SyntheticBadge } from '../components/small';
import { api, setCsrf } from '../lib/api';
import { useI18n } from '../lib/i18n';
import { PatternMap as MapView, type MapData } from '../features/map';

export default function PatternMap() {
  const { t, err } = useI18n();
  const [authed, setAuthed] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [data, setData] = useState<MapData | null>(null);
  const [error, setError] = useState('');

  const load = async () => {
    try { setData(await api('/reports/map')); setError(''); } catch (e) { setError(err(e)); }
  };
  useEffect(() => {
    api<{ authenticated?: boolean; csrf_token?: string }>('/auth/me').then((me) => {
      if (me.authenticated) { setCsrf(me.csrf_token ?? ''); setAuthed(true); void load(); }
    }).catch(() => { /* stay on login form */ });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (e: FormEvent) => {
    e.preventDefault(); setError('');
    try {
      const r = await api<{ csrf_token?: string }>('/auth/login', { email, password });
      setCsrf(r.csrf_token ?? ''); setPassword(''); setAuthed(true); await load();
    } catch (x) { setError(err(x)); }
  };
  const logout = async () => {
    try { await api('/auth/logout', {}); } catch { /* ignore */ }
    setCsrf(''); setAuthed(false); setData(null);
  };

  return (
    <div className="stack">
      <h1>{t('map.title')} <SyntheticBadge label={t('map.synthetic_badge')} /></h1>
      {!authed ? (
        <form className="card stack" onSubmit={login}>
          <p>{t('map.login_required')}</p>
          <label htmlFor="m-email">{t('map.email')}</label>
          <input id="m-email" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
          <label htmlFor="m-pw">{t('map.password')}</label>
          <input id="m-pw" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="btn btn-primary" type="submit">{t('map.sign_in')}</button>
        </form>
      ) : (
        <>
          <button className="btn" type="button" onClick={() => void logout()}>{t('map.sign_out')}</button>
          {data && <MapView data={data} labels={{ title: t('map.title'), syntheticData: t('map.synthetic_badge'), repeatedAgents: t('map.repeated_agents'), repeatedTemplates: t('map.repeated_templates'), reports: t('map.reports') }} />}
        </>
      )}
      <ErrorNote message={error} />
    </div>
  );
}
