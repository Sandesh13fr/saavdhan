import { AlertCircle, ChevronLeft, ChevronRight, ExternalLink, FileText, MessageSquareText, MessageCircleQuestion, UserRound } from 'lucide-react';
import { useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { DemoChip, Disclosure, Headline, PillLink, QuoteBlock } from '../components/ui';
import { packetUrl } from '../lib/api';
import { ruleText, sortHits, uniqueEvidence } from '../lib/caseUtils';
import { useI18n } from '../lib/i18n';
import type { CaseView } from '../lib/types';
import { Loading } from './common';

interface Src { id: string; file: string; line?: number | null; page?: number | null; text: string }

const CHAT = /^\[([^\]]+)\]\s*([^:]{1,60}):\s*(.*)$/s;

function mark(text: string, quotes: string[]): ReactNode {
  const q = quotes.find((x) => x && text.includes(x));
  if (!q) return text;
  const i = text.indexOf(q);
  return <>{text.slice(0, i)}<mark>{q}</mark>{text.slice(i + q.length)}</>;
}

export default function Evidence({ view }: { view: CaseView | null }) {
  const { t } = useI18n();
  const [idx, setIdx] = useState(0);
  const wrap = useRef<HTMLDivElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const card = useRef<HTMLDivElement>(null);
  const [path, setPath] = useState('');

  const a = view?.analysis;
  const flagged = a ? sortHits(a.verdict.rule_hits).filter((h) => h.status === 'hit') : [];
  const current = flagged[Math.min(idx, Math.max(flagged.length - 1, 0))];
  const ev = current ? uniqueEvidence(current) : [];
  const refs = new Set(ev.map((e) => e.source_ref));
  const quotes = ev.map((e) => e.quote);

  const all = (view?.sources ?? []) as unknown as Src[];
  const lines = all.filter((s) => s.line != null || s.page != null);
  const shown = lines.length ? lines : all;
  const isHit = (s: Src) => refs.has(s.id) || quotes.some((q) => q && s.text.includes(q));

  // Connector from the first highlighted line to the rule card (side-by-side layouts only).
  useLayoutEffect(() => {
    const draw = () => {
      const w = wrap.current; const p = panel.current; const c = card.current;
      const target = p?.querySelector('.bubble.is-hit') as HTMLElement | null;
      if (!w || !p || !c || !target) { setPath(''); return; }
      const W = w.getBoundingClientRect(); const B = target.getBoundingClientRect(); const C = c.getBoundingClientRect(); const P = p.getBoundingClientRect();
      if (C.left < B.right + 24 || B.top < P.top - 4 || B.bottom > P.bottom + 4) { setPath(''); return; }
      const x1 = B.right - W.left; const y1 = B.top + B.height / 2 - W.top;
      const x2 = C.left - W.left; const y2 = C.top + 60 - W.top;
      const mx = (x1 + x2) / 2;
      setPath(`M${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`);
    };
    const target = panel.current?.querySelector('.bubble.is-hit') as HTMLElement | null;
    if (target && panel.current) {
      const p = panel.current;
      const top = target.offsetTop - p.clientHeight / 2 + target.clientHeight / 2;
      p.scrollTo({ top: Math.max(0, top), behavior: 'auto' });
    }
    draw();
    const ro = new ResizeObserver(draw);
    if (wrap.current) ro.observe(wrap.current);
    const p = panel.current;
    p?.addEventListener('scroll', draw, { passive: true });
    addEventListener('resize', draw);
    return () => { ro.disconnect(); p?.removeEventListener('scroll', draw); removeEventListener('resize', draw); };
  }, [idx, view?.id, current?.rule_id]);

  if (!view) return <Loading />;
  if (!a) return <Loading text={t('review.not_analyzed')} />;
  const raDate = a.verdict.ra_list_date;
  const fileName = shown[0]?.file ?? '';

  return (
    <div className="page evidence">
      <div className="evidence__grid" ref={wrap}>
        <section className="chat-card card enter" aria-labelledby="offer-h">
          <header className="chat-card__head">
            <MessageSquareText size={26} strokeWidth={1.7} aria-hidden="true" />
            <h2 id="offer-h">{t('evidence.offer_text')}</h2>
            <span className="mono small muted chat-card__file">{fileName}</span>
          </header>
          <div className="chat-card__body" ref={panel} tabIndex={0} aria-label={t('evidence.offer_text')}>
            <ol className="bubbles">
              {shown.map((s) => {
                const m = s.text.match(CHAT);
                const hit = isHit(s);
                if (!s.text.trim()) return null;
                return (
                  <li key={s.id} className={`bubble-row ${hit ? 'is-hit' : ''}`}>
                    <span className="bubble-row__avatar" aria-hidden="true"><UserRound size={20} /></span>
                    <div className={`bubble ${hit ? 'is-hit' : ''}`}>
                      {m && <span className="bubble__meta">{m[2]} · {m[1]}</span>}
                      <p lang="und">{mark(m ? m[3] : s.text, hit ? quotes : [])}</p>
                      <span className="bubble__ref mono">{s.id}</span>
                      {hit && <span className="bubble__pin" aria-hidden="true" />}
                      {hit && <span className="sr-only">{t('evidence.quoted_line')}</span>}
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>
        </section>

        {path && <svg className="connector" aria-hidden="true"><path d={path} /></svg>}

        <section className="evidence__side enter-2" aria-labelledby="evidence-h">
          {view.demo && <div className="chip-row" style={{ marginBottom: 14 }}><DemoChip /></div>}
          <Headline id="evidence-h" size="md" text={t('evidence.title')} />
          {current ? (
            <>
              <div className="flag-nav" aria-live="polite">
                <span className="small muted">{t('evidence.counter', { n: Math.min(idx, flagged.length - 1) + 1, total: flagged.length })}</span>
                <div className="flag-nav__btns">
                  <button type="button" className="icon-btn icon-btn--ring" onClick={() => setIdx((i) => Math.max(0, i - 1))} disabled={idx === 0} aria-label={t('evidence.prev')}><ChevronLeft size={22} aria-hidden="true" /></button>
                  <button type="button" className="icon-btn icon-btn--ring" onClick={() => setIdx((i) => Math.min(flagged.length - 1, i + 1))} disabled={idx >= flagged.length - 1} aria-label={t('evidence.next')}><ChevronRight size={22} aria-hidden="true" /></button>
                </div>
              </div>
              <div className="flag-card" ref={card}>
                <span className="flag-card__icon" aria-hidden="true"><AlertCircle size={30} strokeWidth={2.2} /></span>
                <div>
                  <h2>{t(`rule.${current.rule_id}.title`)}</h2>
                  <p>{ruleText(current, t, raDate)}</p>
                  {!ev.length && <p className="small flag-card__note">{t('evidence.no_quote')}</p>}
                </div>
              </div>
              <div className="rows" style={{ marginTop: 14 }}>
                <Disclosure key={`ref-${current.rule_id}`} icon={<span className="row__icon" aria-hidden="true"><FileText size={24} strokeWidth={1.7} /></span>} title={t('evidence.rule_reference')}>
                  <p className="meta-line">
                    <span className={`badge badge--${current.status}`}>{t(`verdict.status.${current.status}`)}</span>
                    <span className="badge">{t('result.severity')}: {t(`severity.${current.severity}`)}</span>
                    {current.heuristic && <span className="badge badge--heur">{t('verdict.heuristic_badge')}</span>}
                  </p>
                  {ev.map((f, i) => <QuoteBlock key={i} field={f} />)}
                  {!current.heuristic && /^https?:\/\//.test(current.rule_source_url)
                    ? <a className="src-link" href={current.rule_source_url} target="_blank" rel="noreferrer noopener">{t('verdict.rule_source')} <ExternalLink size={16} aria-hidden="true" /><span className="sr-only"> ({t('ui.new_tab')})</span></a>
                    : <p className="small muted">{t('evidence.heuristic_note')}</p>}
                </Disclosure>
                <Disclosure key={`ask-${current.rule_id}`} icon={<span className="row__icon" aria-hidden="true"><MessageCircleQuestion size={24} strokeWidth={1.7} /></span>} title={t('evidence.ask_next')}>
                  <p>{t(a.verdict.next_steps_key)}</p>
                </Disclosure>
              </div>
            </>
          ) : <p className="lede lede--muted">{t('evidence.none')}</p>}
          <div className="actions">
            <PillLink href={packetUrl(view.id)} download wide>{t('evidence.download')}</PillLink>
          </div>
          <p className="small muted" style={{ marginTop: 14 }}><a href={`#/result/${view.id}`}>{t('evidence.back')}</a></p>
        </section>
      </div>
    </div>
  );
}
