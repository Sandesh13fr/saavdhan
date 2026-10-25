import { BellRing, Download } from 'lucide-react';
import { packetUrl } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView } from '../lib/types';

export default function FamilyPhone({ view }: { view: CaseView | null }) {
  const { t } = useI18n();
  const alerts = view?.safety?.alerts ?? [];
  return (
    <div className="stack">
      <h1>{t('family.title')}</h1>
      <div className="phone" role="region" aria-label={t('family.title')}>
        <div className="phone-bar"><span className="badge badge-synthetic">{t('family.simulated_badge')}</span></div>
        <div className="phone-body">
          {!view || alerts.length === 0 ? <p className="muted">{t('family.no_alerts')}</p> : alerts.map((a, i) => (
            <article key={i} className="alert-card">
              <h2><BellRing size={18} aria-hidden="true" /> {t('family.alert_title')}</h2>
              <p>{t(a.message_key, { alias: view.safety?.plan.traveller_alias ?? a.to_alias })}</p>
              <p className="muted">{a.to_alias} · {a.channel} · {new Date(a.at).toLocaleString()}</p>
              <a className="btn" href={packetUrl(view.id)} download><Download size={16} aria-hidden="true" /> {t('family.open_packet')}</a>
            </article>
          ))}
        </div>
      </div>
      <p className="muted">{t('safety.simulated_note')}</p>
    </div>
  );
}
