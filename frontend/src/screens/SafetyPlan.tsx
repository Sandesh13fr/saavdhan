import { CheckCircle2, Clock, AlertTriangle, Plus, Trash2 } from 'lucide-react';
import { useState, type FormEvent } from 'react';
import { ErrorNote, SyntheticBadge } from '../components/small';
import { api } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, Contact } from '../lib/types';

const when = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? iso : d.toLocaleString(); };
const STATUS_ICON = { ok: CheckCircle2, due: Clock, missed: AlertTriangle };

export default function SafetyPlan({ view, onCase }: { view: CaseView | null; onCase: (c: CaseView) => void }) {
  const { t, err } = useI18n();
  const plan = view?.safety?.plan;
  const [alias, setAlias] = useState(plan?.traveller_alias ?? '');
  const [contacts, setContacts] = useState<Contact[]>(plan?.contacts ?? [{ alias: '', channel: '' }]);
  const [itinerary, setItinerary] = useState((plan?.itinerary ?? []).join('\n'));
  const [hours, setHours] = useState(plan?.checkin_interval_hours ?? 24);
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (!view) return <p>{t('verdict.not_found')}</p>;
  const act = async (call: () => Promise<CaseView>) => {
    setBusy(true); setError('');
    try { onCase(await call()); } catch (e) { setError(err(e)); } finally { setBusy(false); }
  };
  const save = (e: FormEvent) => {
    e.preventDefault();
    void act(() => api<CaseView>(`/offers/${view.id}/safety-plan`, {
      traveller_alias: alias.trim(),
      contacts: contacts.filter((c) => c.alias.trim() && c.channel.trim()).slice(0, 2),
      itinerary: itinerary.split('\n').map((s) => s.trim()).filter(Boolean),
      checkin_interval_hours: hours,
    }));
  };
  const setContact = (i: number, patch: Partial<Contact>) => setContacts(contacts.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  const s = view.safety;
  const Icon = s ? STATUS_ICON[s.status] : Clock;
  const last = s?.checkins.at(-1);

  return (
    <div className="stack">
      <h1>{t('safety.title')} {view.demo && <SyntheticBadge />}</h1>
      <p>{t('safety.intro')}</p>
      <p className="muted">{t('safety.simulated_note')}</p>
      <form className="card stack" onSubmit={save} aria-busy={busy}>
        <label htmlFor="sp-alias">{t('safety.traveller_alias')}</label>
        <input id="sp-alias" required maxLength={60} value={alias} onChange={(e) => setAlias(e.target.value)} />
        {contacts.map((c, i) => (
          <fieldset key={i} className="stack">
            <legend>{t('safety.contact_alias')} {i + 1}</legend>
            <label htmlFor={`sp-ca-${i}`}>{t('safety.contact_alias')}</label>
            <input id={`sp-ca-${i}`} maxLength={60} value={c.alias} onChange={(e) => setContact(i, { alias: e.target.value })} />
            <label htmlFor={`sp-cc-${i}`}>{t('safety.contact_channel')}</label>
            <input id={`sp-cc-${i}`} maxLength={120} value={c.channel} onChange={(e) => setContact(i, { channel: e.target.value })} />
            {contacts.length > 1 && (
              <button type="button" className="btn btn-quiet" onClick={() => setContacts(contacts.filter((_, j) => j !== i))}>
                <Trash2 size={16} aria-hidden="true" /> {t('safety.remove_contact')}
              </button>
            )}
          </fieldset>
        ))}
        {contacts.length < 2 && (
          <button type="button" className="btn" onClick={() => setContacts([...contacts, { alias: '', channel: '' }])}>
            <Plus size={16} aria-hidden="true" /> {t('safety.add_contact')}
          </button>
        )}
        <label htmlFor="sp-it">{t('safety.itinerary')}</label>
        <textarea id="sp-it" rows={4} value={itinerary} placeholder={t('safety.itinerary_placeholder')} onChange={(e) => setItinerary(e.target.value)} />
        <label htmlFor="sp-h">{t('safety.interval_hours')}</label>
        <input id="sp-h" type="number" min={1} max={168} value={hours} onChange={(e) => setHours(Math.max(1, Number(e.target.value) || 24))} />
        <button className="btn btn-primary" type="submit" disabled={busy || !alias.trim() || !contacts[0]?.alias.trim() || !contacts[0]?.channel.trim()}>{t('safety.save')}</button>
      </form>
      <ErrorNote message={error} />
      {s && (
        <section className={`card stack status status-${s.status}`} aria-labelledby="st-h">
          <h2 id="st-h"><Icon size={20} aria-hidden="true" /> {t(`safety.status.${s.status}`)}</h2>
          <p>{t('safety.next_due', { time: when(s.next_due) })}</p>
          {last && <p>{t('safety.last_checkin', { time: when(last.at) })}{last.note ? `: ${last.note}` : ''}</p>}
          <label htmlFor="ci-note">{t('safety.checkin_note')}</label>
          <input id="ci-note" maxLength={200} value={note} onChange={(e) => setNote(e.target.value)} />
          <div className="row">
            <button className="btn btn-primary" type="button" disabled={busy}
              onClick={() => void act(async () => { const v = await api<CaseView>(`/offers/${view.id}/checkin`, { note }); setNote(''); return v; })}>
              {t('safety.checkin')}
            </button>
            {view.demo && (
              <button className="btn" type="button" disabled={busy}
                onClick={() => void act(() => api<CaseView>('/demo/advance-clock', { case_id: view.id, hours: 24 }))}>
                {t('safety.demo_advance')}
              </button>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
