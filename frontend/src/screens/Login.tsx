import { Eye, EyeOff, Info, Lock, Mail } from 'lucide-react';
import { useEffect, useState, type FormEvent } from 'react';
import { PatternNodes } from '../components/Illustrations';
import { ErrorNote, Headline, PillButton } from '../components/ui';
import { api, setCsrf } from '../lib/api';
import { useI18n } from '../lib/i18n';
import { go } from '../lib/route';

export default function Login({ authed, onAuthed }: { authed: boolean; onAuthed: () => void }) {
  const { t, err } = useI18n();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => { if (authed) go('map'); }, [authed]);

  const login = async (e: FormEvent) => {
    e.preventDefault(); setError(''); setBusy(true);
    try {
      const r = await api<{ csrf_token?: string }>('/auth/login', { email, password });
      setCsrf(r.csrf_token ?? ''); setPassword(''); onAuthed();
    } catch (x) { setError(err(x)); } finally { setBusy(false); }
  };

  return (
    <div className="page login">
      <div className="split">
        <section className="enter" aria-labelledby="login-hero">
          <Headline id="login-hero" as="h2" size="md" text={t('login.hero')} />
          <div className="login__art" aria-hidden="true"><PatternNodes /></div>
          <p className="small muted login__note"><Info size={20} aria-hidden="true" /> {t('map.synthetic_badge')}</p>
        </section>
        <form className="card login__card enter-2" onSubmit={login} aria-labelledby="login-h" aria-busy={busy}>
          <p className="muted login__restricted"><Lock size={24} strokeWidth={1.7} aria-hidden="true" /> {t('login.restricted')}</p>
          <h1 id="login-h" className="headline headline--sm">{t('login.title')}</h1>
          <p className="muted small">{t('map.login_required')}</p>
          <label className="icon-field">
            <span className="sr-only">{t('map.email')}</span>
            <Mail size={22} strokeWidth={1.7} aria-hidden="true" />
            <input className="input" type="email" autoComplete="username" required value={email} placeholder={t('map.email')} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="icon-field">
            <span className="sr-only">{t('map.password')}</span>
            <Lock size={22} strokeWidth={1.7} aria-hidden="true" />
            <input className="input" type={show ? 'text' : 'password'} autoComplete="current-password" required value={password} placeholder={t('map.password')} onChange={(e) => setPassword(e.target.value)} />
            <button type="button" className="icon-btn icon-field__toggle" aria-pressed={show} aria-label={t('login.show_password')} onClick={() => setShow(!show)}>
              {show ? <EyeOff size={22} aria-hidden="true" /> : <Eye size={22} aria-hidden="true" />}
            </button>
          </label>
          <ErrorNote message={error} />
          <PillButton type="submit" tone="red" wide busy={busy} disabled={busy}>{t('login.cta')}</PillButton>
        </form>
      </div>
    </div>
  );
}
