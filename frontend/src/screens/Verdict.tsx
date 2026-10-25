import { Download } from 'lucide-react';
import { RuleHitCard } from '../components/RuleHitCard';
import { SyntheticBadge, VerdictBanner } from '../components/small';
import { packetUrl } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, FieldValue } from '../lib/types';

const STATUS_ORDER = { hit: 0, unknown: 1, clear: 2 };
const SEV_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };

const pretty = (name: string) => name.replaceAll('_', ' ');

export default function Verdict({ view, onPlan }: { view: CaseView | null; onPlan: () => void }) {
  const { t } = useI18n();
  const a = view?.analysis;
  if (!view || !a) return <p>{t('verdict.not_found')}</p>;
  const { verdict, offer } = a;
  const hits = [...verdict.rule_hits].sort((x, y) =>
    STATUS_ORDER[x.status] - STATUS_ORDER[y.status] || SEV_ORDER[x.severity] - SEV_ORDER[y.severity]);
  const facts = Object.entries(offer).flatMap(([name, v]): [string, FieldValue][] => {
    if (name === 'source_ids' || !Array.isArray(v)) return v && typeof v === 'object' && !Array.isArray(v) && (v as FieldValue).value != null ? [[name, v as FieldValue]] : [];
    return (v as FieldValue[]).filter((f) => f && typeof f === 'object' && f.value != null).map((f): [string, FieldValue] => [name, f]);
  });

  return (
    <div className="stack">
      {view.demo && <p><SyntheticBadge /></p>}
      <VerdictBanner level={verdict.level} raDate={verdict.ra_list_date} />
      <p className="next">{t(verdict.next_steps_key)}</p>
      <div className="row">
        <a className="btn" href={packetUrl(view.id)} download><Download size={18} aria-hidden="true" /> {t('verdict.download_packet')}</a>
        <button className="btn btn-primary" type="button" onClick={onPlan}>{t('verdict.make_safety_plan')}</button>
      </div>
      <ul className="plain stack">{hits.map((h) => <RuleHitCard key={h.rule_id} hit={h} raDate={verdict.ra_list_date} />)}</ul>
      <section className="card" aria-labelledby="facts-h">
        <h2 id="facts-h">{t('verdict.facts_title')}</h2>
        <p className="muted">{t(`verdict.method.${a.extraction_method}`)}</p>
        <div className="table-wrap">
          <table>
            <tbody>
              {facts.map(([name, f], i) => (
                <tr key={name + i}>
                  <th scope="row">{t(`field.${name}`) === `field.${name}` ? pretty(name) : t(`field.${name}`)}</th>
                  <td>{f.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {a.errors.length > 0 && <ul className="muted">{a.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>}
      </section>
    </div>
  );
}
