import { AlertCircle, Check, ChevronDown, Download, ExternalLink, HelpCircle, Info } from 'lucide-react';
import { useState } from 'react';
import { OfferDoc, StopSign, VerifyIllo } from '../components/Illustrations';
import { DemoChip, Headline, PillLink, QuoteBlock } from '../components/ui';
import { isListDate, ruleIcon, ruleText, sortHits, uniqueEvidence } from '../lib/caseUtils';
import { packetUrl } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView, Level, RuleHit } from '../lib/types';
import { Loading } from './common';

function RuleRow({ hit, raDate }: { hit: RuleHit; raDate: string }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const Icon = ruleIcon(hit.rule_id);
  const id = `rule-${hit.rule_id}`;
  const isUrl = /^https?:\/\//.test(hit.rule_source_url);
  const Flag = hit.status === 'hit' ? AlertCircle : hit.status === 'unknown' ? HelpCircle : Check;
  return (
    <li className={`row row--${hit.status}`}>
      <button type="button" className="row__head" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}>
        <span className="row__icon" aria-hidden="true">
          <Icon size={26} strokeWidth={1.7} />
          <span className={`row__flag row__flag--${hit.status}`}><Flag size={14} strokeWidth={2.6} /></span>
        </span>
        <span className="row__title">
          <strong>{t(`rule.${hit.rule_id}.title`)}</strong>
          <span><span className={hit.status === 'hit' ? 't-hit' : undefined}>{t(`verdict.status.${hit.status}`)}</span> · {t(`severity.${hit.severity}`)}</span>
        </span>
        <ChevronDown className="row__chev" size={24} aria-hidden="true" />
      </button>
      <div id={id} className="row__body" hidden={!open}>
        <p>{ruleText(hit, t, raDate)}</p>
        <p className="meta-line">
          <span className={`badge badge--${hit.status}`}>{t(`verdict.status.${hit.status}`)}</span>
          <span className="badge">{t('result.severity')}: {t(`severity.${hit.severity}`)}</span>
          {hit.heuristic && <span className="badge badge--heur">{t('verdict.heuristic_badge')}</span>}
        </p>
        {uniqueEvidence(hit).map((f, i) => <QuoteBlock key={i} field={f} />)}
        {!hit.heuristic && isUrl && (
          <a className="src-link" href={hit.rule_source_url} target="_blank" rel="noreferrer noopener">
            {t('verdict.rule_source')} <ExternalLink size={16} aria-hidden="true" /><span className="sr-only"> ({t('ui.new_tab')})</span>
          </a>
        )}
      </div>
    </li>
  );
}

export function VerdictStrip({ level, raDate }: { level: Level; raDate: string }) {
  const { t } = useI18n();
  return (
    <div className={`verdict-strip verdict-strip--${level}`}>
      <span className="verdict-strip__tag">{t(`result.tag.${level}`)}</span>
      <div className="verdict-strip__body">
        <p>{t(`verdict.${level}.body`)}</p>
        <p className="ra-line">{isListDate(raDate) ? t('verdict.ra_list_date', { date: raDate }) : t('verdict.ra_not_checked')}</p>
      </div>
    </div>
  );
}

export default function Result({ view }: { view: CaseView | null }) {
  const { t } = useI18n();
  const [showClear, setShowClear] = useState(false);
  if (!view) return <Loading />;
  const a = view.analysis;
  if (!a) return <Loading text={t('review.not_analyzed')} />;
  const { level, ra_list_date: raDate } = a.verdict;
  const sorted = sortHits(a.verdict.rule_hits);
  const open = sorted.filter((h) => h.status !== 'clear');
  const clear = sorted.filter((h) => h.status === 'clear');
  const firstQuote = sorted.find((h) => h.status === 'hit' && uniqueEvidence(h).length);
  const flagLabel = firstQuote ? t(`rule.${firstQuote.rule_id}.title`) : '';

  const heading = level === 'STOP' ? (
    <>
      <div className="result__stop-art"><StopSign size={210} /></div>
      <h1 id="result-h" className="headline headline--xl result__word">{t('result.word.STOP')}<span className="sr-only">: {t('verdict.STOP.title')}</span></h1>
    </>
  ) : level === 'VERIFY_FIRST' ? (
    <h1 id="result-h" className="headline headline--xl result__verify">
      <span className="line">{t('result.word.VERIFY')}</span><span className="line result__first">{t('result.word.FIRST')}</span>
      <span className="sr-only">: {t('verdict.VERIFY_FIRST.title')}</span>
    </h1>
  ) : <Headline id="result-h" size="xl" text={t('result.word.NO_RED_FLAGS_FOUND')} />;

  return (
    <div className="page result">
      <div className={`split split--top result--${level}`}>
        <section aria-labelledby="result-h" className={`result__main enter ${level === 'STOP' ? 'is-centered' : ''}`}>
          {view.demo && <div className="chip-row result__chips"><DemoChip /></div>}
          {heading}
          <p className="lede result__sub">{t(`result.sub.${level}`)}</p>
          <VerdictStrip level={level} raDate={raDate} />

          {open.length > 0 && (
            <>
              <h2 className="sr-only">{t('result.points_heading')}</h2>
              <ul className="rows result__rows">{open.map((h) => <RuleRow key={h.rule_id} hit={h} raDate={raDate} />)}</ul>
            </>
          )}
          {level === 'NO_RED_FLAGS_FOUND' && (
            <p className="note-box"><Info size={22} aria-hidden="true" /> <span>{t('result.not_clearance')}</span>{view.demo && <span className="note-box__demo">{t('ui.demo_data')}</span>}</p>
          )}
          {clear.length > 0 && (
            <div className="result__clear">
              <button type="button" className="group-toggle" aria-expanded={showClear} aria-controls="clear-rows" onClick={() => setShowClear(!showClear)}>
                <Check size={20} aria-hidden="true" /> {t('result.passed', { count: clear.length })}
                <ChevronDown className="row__chev" size={22} aria-hidden="true" />
              </button>
              <ul className="rows" id="clear-rows" hidden={!showClear}>{clear.map((h) => <RuleRow key={h.rule_id} hit={h} raDate={raDate} />)}</ul>
            </div>
          )}

          <div className="actions">
            <PillLink href={`#/evidence/${view.id}`}>{level === 'NO_RED_FLAGS_FOUND' ? t('result.cta_report') : t('result.cta_evidence')}</PillLink>
            <span className="vsep" aria-hidden="true" />
            {level === 'NO_RED_FLAGS_FOUND'
              ? <a className="link-btn" href={`#/plan/${view.id}`}>{t('result.plan_checkins')}</a>
              : <a className="link-btn" href={`#/help/${view.id}`}>{t('result.get_help')}</a>}
          </div>
          <div className="secondary-actions">
            <a className="ghost-btn ghost-btn--sm" href={packetUrl(view.id)} download><Download size={18} aria-hidden="true" /> {t('verdict.download_packet')}</a>
            {level !== 'NO_RED_FLAGS_FOUND'
              ? <a className="ghost-btn ghost-btn--sm" href={`#/plan/${view.id}`}>{t('verdict.make_safety_plan')}</a>
              : <a className="ghost-btn ghost-btn--sm" href={`#/help/${view.id}`}>{t('result.get_help')}</a>}
          </div>
        </section>
        <div className="result__art enter-2" aria-hidden="true">
          {level === 'STOP' && <OfferDoc title={t('illo.job_offer')} demo={view.demo ? t('ui.demo_data') : ''} flagRow={flagLabel || t('result.tag.STOP')} magnifier="none" rotate={5} />}
          {level === 'VERIFY_FIRST' && <VerifyIllo />}
          {level === 'NO_RED_FLAGS_FOUND' && <OfferDoc title="" demo="" magnifier="ink" rotate={4} />}
        </div>
      </div>
      <footer className="result-foot">
        <span>{t('result.foot_confirm')}</span>
        <a href={`#/evidence/${view.id}`}>{t('result.foot_quotes')}</a>
      </footer>
    </div>
  );
}
