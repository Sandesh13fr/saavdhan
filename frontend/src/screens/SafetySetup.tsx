import { ChevronDown, Luggage, UserRound } from 'lucide-react';
import { useState, type FormEvent } from 'react';
import { ClockGlyph, ClockRing } from '../components/Illustrations';
import { AlertChip, ErrorNote, Headline, PillButton } from '../components/ui';
import { api } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, Contact } from '../lib/types';
import { go } from '../lib/route';
import { Loading, NeedCase } from './common';

const INTERVALS = [6, 12, 24, 48, 72];

export default function SafetySetup({ view, caseId, onCase }: { view: CaseView | null; caseId: string; onCase: (c: CaseView) => void }) {
  const { t, err } = useI18n();
  const plan = view?.safety?.plan;
  const [alias, setAlias] = useState(plan?.traveller_alias ?? '');
  const [contacts, setContacts] = useState<Contact[]>(() => {
    const c = plan?.contacts ?? [];
    return [c[0] ?? { alias: '', channel: '' }, c[1] ?? { alias: '', channel: '' }];
  });
  const [itinerary, setItinerary] = useState((plan?.itinerary ?? []).join('\n'));
  const [hours, setHours] = useState(plan?.checkin_interval_hours ?? 24);
  const [consent, setConsent] = useState(!!plan);
  const [trip, setTrip] = useState(!!plan?.itinerary.length);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (!caseId) return <NeedCase title={t('plan.need_title')} body={t('plan.need_body')} />;
  if (!view) return <Loading />;

  const filled = contacts.filter((c) => c.alias.trim() && c.channel.trim());
  const half = contacts.some((c) => !!c.alias.trim() !== !!c.channel.trim());
  const ready = alias.trim() && filled.length > 0 && !half && consent;
  const setContact = (i: number, patch: Partial<Contact>) => setContacts(contacts.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  const save = async (e: FormEvent) => {
    e.preventDefault();
    if (!ready) return;
    setBusy(true); setError('');
    try {
      onCase(await api<CaseView>(`/offers/${view.id}/safety-plan`, {
        traveller_alias: alias.trim(),
        contacts: filled.map((c) => ({ alias: c.alias.trim(), channel: c.channel.trim() })).slice(0, 2),
        itinerary: itinerary.split('\n').map((s) => s.trim()).filter(Boolean),
        checkin_interval_hours: hours,
      }));
      go('checkin', view.id);
    } catch (x) { setError(err(x)); } finally { setBusy(false); }
  };

  return (
    <div className="page plan">
      <form className="plan__grid" onSubmit={save} aria-labelledby="plan-h" aria-busy={busy}>
        <div className="plan__main enter">
          <AlertChip>{t('plan.demo_only')}</AlertChip>
          <Headline id="plan-h" size="md" text={t('plan.title')} className="plan__title" />
          <p className="lede">{t('plan.sub')}</p>

          <div className="person-card tile">
            <span className="ico-circle ico-circle--red" aria-hidden="true"><UserRound size={30} strokeWidth={1.7} /></span>
            <div className="person-card__fields">
              <h2>{t('plan.you')}</h2>
              <label className="field"><span className="sr-only">{t('safety.traveller_alias')}</span>
                <input className="input" required maxLength={60} value={alias} placeholder={t('safety.traveller_alias')} onChange={(e) => setAlias(e.target.value)} />
              </label>
            </div>
          </div>
          {contacts.map((c, i) => (
            <fieldset key={i} className="person-card tile">
              <span className="ico-circle ico-circle--red" aria-hidden="true"><UserRound size={30} strokeWidth={1.7} /></span>
              <div className="person-card__fields">
                <legend><h2>{t('plan.contact_n', { n: i + 1 })}{i === 1 && <span className="muted small"> · {t('plan.optional')}</span>}</h2></legend>
                <div className="pair">
                  <label className="field"><span className="sr-only">{t('plan.contact_n', { n: i + 1 })}: {t('safety.contact_alias')}</span>
                    <input className="input" maxLength={60} value={c.alias} placeholder={t('plan.name_placeholder')} onChange={(e) => setContact(i, { alias: e.target.value })} />
                  </label>
                  <label className="field"><span className="sr-only">{t('plan.contact_n', { n: i + 1 })}: {t('safety.contact_channel')}</span>
                    <input className="input" maxLength={120} value={c.channel} placeholder={t('plan.channel_placeholder')} onChange={(e) => setContact(i, { channel: e.target.value })} />
                  </label>
                </div>
              </div>
            </fieldset>
          ))}
          {half && <p className="small" style={{ color: 'var(--alert-deep)' }}>{t('plan.half_contact')}</p>}
          <label className="check" style={{ marginTop: 18 }}>
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} /> {t('plan.permission')}
          </label>
          <p className="small muted">{t('safety.simulated_note')}</p>
          <ErrorNote message={error} />
          <div className="plan__bottom">
            <PillButton type="submit" busy={busy} disabled={busy || !ready}>{t('plan.cta')}</PillButton>
          </div>
        </div>

        <aside className="plan__side enter-2" aria-label={t('plan.interval_label')}>
          <ClockRing fraction={hours / 48} label={t('plan.ring_label', { hours })}>
            <ClockGlyph size={84} />
            <strong className="clock__big tnum">{t('plan.hours_short', { hours })}</strong>
          </ClockRing>
          <label className="field interval">
            <span>{t('plan.every')}</span>
            <span className="select-wrap">
              <select className="select" value={hours} onChange={(e) => setHours(Number(e.target.value))}>
                {INTERVALS.map((h) => <option key={h} value={h}>{t('plan.hours_option', { hours: h })}</option>)}
              </select>
              <ChevronDown size={22} aria-hidden="true" />
            </span>
          </label>
          <div className="row trip-row">
            <button type="button" className="row__head" aria-expanded={trip} aria-controls="trip-body" onClick={() => setTrip(!trip)}>
              <Luggage size={30} strokeWidth={1.6} aria-hidden="true" />
              <span className="row__title"><strong>{t('plan.trip')}</strong></span>
              <ChevronDown className="row__chev" size={24} aria-hidden="true" />
            </button>
            <div id="trip-body" className="row__body" hidden={!trip} style={{ paddingLeft: 22 }}>
              <label className="field"><span>{t('safety.itinerary')}</span>
                <textarea className="textarea" style={{ minHeight: 120 }} value={itinerary} placeholder={t('safety.itinerary_placeholder')} onChange={(e) => setItinerary(e.target.value)} />
              </label>
            </div>
          </div>
        </aside>
      </form>
    </div>
  );
}
