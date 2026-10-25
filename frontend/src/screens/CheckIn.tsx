import { BellRing, ChevronRight, Clock3, FastForward, LifeBuoy, Luggage, UserRound } from 'lucide-react';
import { useState } from 'react';
import { ClockGlyph, ClockRing, FamilyDuo } from '../components/Illustrations';
import { ErrorNote, Headline, PillButton, fmtTime } from '../components/ui';
import { api } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, Lang } from '../lib/types';
import { Loading, NeedCase } from './common';

const dayLabel = (iso: string, nowIso: string, lang: Lang, t: (k: string) => string) => {
  const d = new Date(iso); const n = new Date(nowIso);
  if (isNaN(+d) || isNaN(+n)) return '';
  const day = (x: Date) => Math.floor((+x - x.getTimezoneOffset() * 60000) / 86400000);
  const diff = day(d) - day(n);
  if (diff === 0) return t('checkin.today');
  if (diff === 1) return t('checkin.tomorrow');
  if (diff === -1) return t('checkin.yesterday');
  return d.toLocaleDateString(lang === 'en' ? 'en-IN' : `${lang}-IN`, { day: 'numeric', month: 'short' });
};

export default function CheckIn({ view, caseId, onCase }: { view: CaseView | null; caseId: string; onCase: (c: CaseView) => void }) {
  const { t, err, lang } = useI18n();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');
  const [trip, setTrip] = useState(false);
  const [done, setDone] = useState('');

  if (!caseId) return <NeedCase title={t('plan.need_title')} body={t('plan.need_body')} />;
  if (!view) return <Loading />;
  const s = view.safety;
  if (!s) {
    return (
      <div className="page"><section className="empty">
        <Headline size="sm" text={t('checkin.no_plan_title')} />
        <p className="lede lede--muted">{t('checkin.no_plan_body')}</p>
        <div className="actions"><a className="pill" href={`#/plan/${view.id}`}><span>{t('verdict.make_safety_plan')}</span><span className="pill__arrow" aria-hidden="true"><ChevronRight size={24} /></span></a></div>
      </section></div>
    );
  }

  const act = async (call: () => Promise<CaseView>, msg = '') => {
    setBusy(true); setError(''); setDone('');
    try { onCase(await call()); setDone(msg); } catch (e) { setError(err(e)); } finally { setBusy(false); }
  };
  const interval = s.plan.checkin_interval_hours * 3600000;
  const remaining = +new Date(s.next_due) - +new Date(s.now);
  const fraction = s.status === 'ok' ? remaining / interval : 0;
  const prev = (s.plan as { last_checkin?: string }).last_checkin ?? s.checkins.at(-1)?.at;
  const title = s.status === 'ok' ? t('checkin.title_ok') : s.status === 'due' ? t('checkin.title_due') : t('checkin.title_missed');
  const nContacts = s.plan.contacts.length;

  return (
    <div className="page checkin">
      <div className="checkin__top">
        <Headline size="md" text={title} id="ci-h" className="enter" />
        <span className="chip chip--plain checkin__sim">{t('checkin.simulated')}</span>
      </div>
      {s.status === 'missed' && (
        <p className="error-note checkin__missed" role="status">
          <BellRing size={20} aria-hidden="true" />
          <span>{t('checkin.missed_note')} <a href={`#/family/${view.id}`}>{t('checkin.see_family')}</a></span>
        </p>
      )}
      <div className="checkin__stage">
        <div className="checkin__clock enter-2">
          <ClockRing fraction={fraction} label={t('safety.next_due', { time: fmtTime(s.next_due, lang) })}>
            <ClockGlyph size={72} />
            <strong className="clock__big clock__big--time tnum">{fmtTime(s.next_due, lang)}</strong>
            <span className="muted">{dayLabel(s.next_due, s.now, lang, t)} · {t(`safety.status.${s.status}`)}</span>
          </ClockRing>
        </div>
        <div className="checkin__family enter-3">
          <FamilyDuo />
          <div className="contacts-chip tile">
            <span className="contacts-chip__faces" aria-hidden="true">
              {s.plan.contacts.map((_, i) => <span key={i} className="ico-circle ico-circle--red ico-circle--sm"><UserRound size={22} strokeWidth={1.8} /></span>)}
            </span>
            <span>{t('checkin.contacts', { count: nContacts })}</span>
          </div>
        </div>
      </div>

      <div className="checkin__act">
        <PillButton type="button" busy={busy} disabled={busy} wide onClick={() => void act(async () => { const v = await api<CaseView>(`/offers/${view.id}/checkin`, { note }); setNote(''); return v; }, t('checkin.done'))}>
          {t('checkin.cta')}
        </PillButton>
        <label className="field checkin__note">
          <span className="sr-only">{t('safety.checkin_note')}</span>
          <input className="input" maxLength={200} value={note} placeholder={t('safety.checkin_note')} onChange={(e) => setNote(e.target.value)} />
        </label>
        <p className="sr-only" role="status" aria-live="polite">{done}</p>
        {done && <p className="status-note" aria-hidden="true">{done}</p>}
        <ErrorNote message={error} />
      </div>

      <ul className="quick-tiles">
        <li>
          <button type="button" className="quick tile" aria-expanded={trip} aria-controls="trip-panel" onClick={() => setTrip(!trip)}>
            <Luggage size={32} strokeWidth={1.6} aria-hidden="true" /><span>{t('checkin.trip')}</span><ChevronRight size={22} aria-hidden="true" className={trip ? 'rot90' : ''} />
          </button>
        </li>
        <li><a className="quick tile" href={`#/plan/${view.id}`}><Clock3 size={32} strokeWidth={1.6} aria-hidden="true" /><span>{t('checkin.change_time')}</span><ChevronRight size={22} aria-hidden="true" /></a></li>
        <li><a className="quick tile" href={`#/help/${view.id}`}><LifeBuoy size={32} strokeWidth={1.6} aria-hidden="true" /><span>{t('checkin.get_help')}</span><ChevronRight size={22} aria-hidden="true" /></a></li>
      </ul>
      <div id="trip-panel" className="trip-panel tile" hidden={!trip}>
        <h2>{t('safety.itinerary')}</h2>
        {s.plan.itinerary.length ? <ul>{s.plan.itinerary.map((x, i) => <li key={i}>{x}</li>)}</ul> : <p className="muted">{t('checkin.no_trip')}</p>}
        <p className="small muted">{t('checkin.contacts_list', { names: s.plan.contacts.map((c) => `${c.alias} (${c.channel})`).join(', ') })}</p>
      </div>

      <div className="timeline" aria-label={t('checkin.timeline')} role="group">
        <div className="timeline__pt">
          <span className="timeline__dot" aria-hidden="true" />
          <span><span className="muted small">{t('checkin.previous')}</span><br />{prev ? `${dayLabel(prev, s.now, lang, t)}, ${fmtTime(prev, lang)}` : '—'}</span>
        </div>
        <span className="timeline__now" aria-hidden="true" />
        <div className="timeline__pt">
          <span className="timeline__dot" aria-hidden="true" />
          <span><span className="muted small">{t('checkin.next')}</span><br />{`${dayLabel(s.next_due, s.now, lang, t)}, ${fmtTime(s.next_due, lang)}`}</span>
        </div>
        <span className="chip chip--sm">{t('checkin.simulated')}</span>
      </div>

      {view.demo && (
        <div className="demo-tools">
          <button type="button" className="ghost-btn ghost-btn--sm" disabled={busy} onClick={() => void act(() => api<CaseView>('/demo/advance-clock', { case_id: view.id, hours: 12 }))}>
            <FastForward size={18} aria-hidden="true" /> {t('safety.demo_advance')}
          </button>
          <span className="small muted">{t('safety.simulated_note')}</span>
        </div>
      )}
    </div>
  );
}
