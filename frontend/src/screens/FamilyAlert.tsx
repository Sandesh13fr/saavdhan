import { ChevronDown, ClipboardList, Luggage, Paperclip } from 'lucide-react';
import { useState } from 'react';
import { PhoneAlert } from '../components/Illustrations';
import { AlertChip, Headline, PillLink, fmtDateTime } from '../components/ui';
import { packetUrl } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, FieldValue } from '../lib/types';
import { Loading, NeedCase } from './common';

export default function FamilyAlert({ view, caseId }: { view: CaseView | null; caseId: string }) {
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(true);
  if (!caseId) return <NeedCase title={t('plan.need_title')} body={t('plan.need_body')} />;
  if (!view) return <Loading />;
  const s = view.safety;
  const alerts = s?.alerts ?? [];
  const traveller = s?.plan.traveller_alias ?? '';
  const country = (view.analysis?.offer.destination_country as FieldValue | undefined)?.value;
  const has = alerts.length > 0;

  return (
    <div className="page family">
      <div className="split">
        <section className="enter" aria-labelledby="fam-h">
          <div className="chip-row"><AlertChip>{t('family2.simulated')}</AlertChip><span className="chip chip--plain">{t('family2.phone_view')}</span></div>
          <Headline id="fam-h" size="xl" text={has ? t('family2.title') : t('family2.title_none')} className="family__title" />
          <p className="lede lede--muted">{has ? t('family2.sub') : t('family2.sub_none')}</p>
          <div className="actions">
            {has
              ? <PillLink href={packetUrl(view.id)} download>{t('family2.cta_report')}</PillLink>
              : <PillLink href={s ? `#/checkin/${view.id}` : `#/plan/${view.id}`}>{s ? t('family2.back_checkin') : t('verdict.make_safety_plan')}</PillLink>}
            <a className="ghost-btn" href={`#/help/${view.id}`}><ClipboardList size={22} strokeWidth={1.7} aria-hidden="true" /> {t('family2.reporting')}</a>
          </div>
        </section>
        <div className="family__art enter-2" aria-hidden="true"><PhoneAlert /></div>
      </div>

      {s && (
        <div className="alert-card tile">
          <button type="button" className="alert-card__head" aria-expanded={open} aria-controls="alert-list" onClick={() => setOpen(!open)}>
            <span className="ico-circle ico-circle--red" aria-hidden="true"><Luggage size={28} strokeWidth={1.6} /></span>
            <span className="alert-card__who">
              <strong>{traveller}{country && <><span className="red-dot" aria-hidden="true" /> {country}</>}</strong>
              <span className="muted">{t(`safety.status.${s.status}`)} · {view.demo ? t('ui.demo_data') : t('family2.simulated')}</span>
            </span>
            <ChevronDown className="row__chev" size={24} aria-hidden="true" />
          </button>
          <a className="alert-card__zip" href={packetUrl(view.id)} download><Paperclip size={22} aria-hidden="true" /> {t('family.open_packet')}</a>
          <div id="alert-list" className="alert-card__body" hidden={!open}>
            {has ? (
              <ol className="alert-list">
                {alerts.map((a, i) => (
                  <li key={i}>
                    <p className="alert-list__title"><span className="badge badge--hit">{t('family.simulated_badge')}</span> <strong>{t('family.alert_title')}</strong></p>
                    <p>{t(a.message_key, { alias: traveller || a.to_alias })}</p>
                    <p className="small muted mono">{t('family2.to', { alias: a.to_alias, channel: a.channel })} · {fmtDateTime(a.at, lang)}</p>
                  </li>
                ))}
              </ol>
            ) : <p className="muted">{t('family.no_alerts')}</p>}
            <p className="small muted">{t('safety.simulated_note')}</p>
          </div>
        </div>
      )}
    </div>
  );
}
