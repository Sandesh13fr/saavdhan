import { CheckCircle2, CircleHelp, Flag, ExternalLink } from 'lucide-react';
import { useI18n } from '../lib/i18n';
import type { RuleHit } from '../lib/types';
import { QuoteBlock } from './small';

const ICON = { hit: Flag, clear: CheckCircle2, unknown: CircleHelp };

export function RuleHitCard({ hit }: { hit: RuleHit }) {
  const { t } = useI18n();
  const Icon = ICON[hit.status];
  const isUrl = /^https?:\/\//.test(hit.rule_source_url);
  return (
    <li className={`rule rule-${hit.status}`}>
      <div className="rule-head">
        <Icon size={20} aria-hidden="true" />
        <h3>{t(`rule.${hit.rule_id}.title`)}</h3>
      </div>
      <p className="chips">
        <span className={`badge badge-${hit.status}`}>{t(`verdict.status.${hit.status}`)}</span>
        <span className="badge">{t(`severity.${hit.severity}`)}</span>
        {hit.heuristic && <span className="badge badge-heuristic">{t('verdict.heuristic_badge')}</span>}
      </p>
      <p>{t(`rule.${hit.rule_id}.${hit.status}`)}</p>
      {hit.evidence.map((f, i) => <QuoteBlock key={i} field={f} />)}
      {!hit.heuristic && isUrl && (
        <a className="rule-src" href={hit.rule_source_url} target="_blank" rel="noreferrer noopener">
          {t('verdict.rule_source')} <ExternalLink size={14} aria-hidden="true" />
        </a>
      )}
    </li>
  );
}
