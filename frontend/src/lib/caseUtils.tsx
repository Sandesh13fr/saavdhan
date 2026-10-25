import {
  BadgeIndianRupee, BookUser, Building2, CircleDollarSign, Contact, FileSignature, FileText, Globe, HeartPulse, IdCard,
  MessageCircle, Plane, Receipt, Timer, TrendingUp, UserRound, UserX, Wallet,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { FieldValue, Offer, RuleHit } from './types';

const STATUS_ORDER = { hit: 0, unknown: 1, clear: 2 };
const SEV_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };

/** hit > unknown > clear, then severity (product rule for result rows). */
export const sortHits = (hits: RuleHit[]) => [...hits].sort((x, y) =>
  STATUS_ORDER[x.status] - STATUS_ORDER[y.status] || SEV_ORDER[x.severity] - SEV_ORDER[y.severity]);

export const uniqueEvidence = (hit: RuleHit) => hit.evidence.filter((f, i, all) =>
  f.quote && all.findIndex((g) => g.quote === f.quote && g.source_ref === f.source_ref) === i);

export const RULE_ICON: Record<string, LucideIcon> = {
  R1_TOURIST_VISA: Globe, R2_RA_NOT_LISTED: UserX, R3_NO_RC_NUMBER: IdCard, R4_FEE_OVER_CAP: BadgeIndianRupee,
  R5_NO_TRIPARTITE_CONTRACT: FileSignature, R6_HIGH_RISK_CORRIDOR: Plane, R7_INFORMAL_CHANNEL_ONLY: MessageCircle,
  R8_NO_RECEIPT: Receipt, R9_PBBY_MISSING: HeartPulse, H1_SALARY_ANOMALY: TrendingUp, H2_PASSPORT_HANDOVER: BookUser,
  H3_PRESSURE: Timer,
};
export const ruleIcon = (id: string) => RULE_ICON[id] ?? FileText;
export const ruleText = (hit: RuleHit, t: (k: string, v?: Record<string, string | number>) => string, raDate: string) =>
  t(`rule.${hit.rule_id}.${hit.status}`, { date: raDate, cap: '35,400' });
export const isListDate = (d: string) => /^\d{4}-\d{2}-\d{2}$/.test(d);

const one = (offer: Offer, name: string) => {
  const v = offer[name];
  return v && !Array.isArray(v) && typeof v === 'object' ? (v as FieldValue) : undefined;
};
const many = (offer: Offer, name: string) => {
  const v = offer[name];
  return Array.isArray(v) ? (v as FieldValue[]).filter((f) => f && typeof f === 'object' && f.value != null) : [];
};

export interface Fact { key: string; icon: LucideIcon; value: string | null; field?: FieldValue }

const inr = (n: string) => `₹${Number(n).toLocaleString('en-IN')}`;

/** Fact tile each rule is about; a tile is flagged when its rule is a critical hit. */
export const RULE_FACT: Record<string, string> = {
  R1_TOURIST_VISA: 'visa', R2_RA_NOT_LISTED: 'agent', R3_NO_RC_NUMBER: 'agent', R4_FEE_OVER_CAP: 'fee',
  R5_NO_TRIPARTITE_CONTRACT: 'contract', R6_HIGH_RISK_CORRIDOR: 'country', R7_INFORMAL_CHANNEL_ONLY: 'channel',
  R8_NO_RECEIPT: 'receipt', R9_PBBY_MISSING: 'pbby', H1_SALARY_ANOMALY: 'salary', H2_PASSPORT_HANDOVER: 'passport',
};

/** Facts for the review tiles: primary six (mock 03) then the rest. Values are shown as the offer gives them. */
export function offerFacts(offer: Offer, t: (k: string) => string): { primary: Fact[]; more: Fact[] } {
  // Normalised tokens (upi, whatsapp, employer...) get a translated label; free text is shown as written.
  const tok = (v: string) => { const k = `value.token.${v}`; const s = t(k); return s === k ? v.charAt(0).toUpperCase() + v.slice(1) : s; };
  const list = (fs: FieldValue[]) => fs.map((f) => tok(String(f.value))).join(', ');
  const yn = (f?: FieldValue) => f?.value == null ? null : f.value === 'yes' ? t('ui.yes') : f.value === 'no' ? t('ui.no') : f.value;
  const agent = one(offer, 'agent_name')?.value ? one(offer, 'agent_name') : one(offer, 'agent_rc_number');
  const visa = one(offer, 'visa_type');
  const salary = one(offer, 'salary_amount');
  const cur = one(offer, 'salary_currency')?.value;
  const fee = one(offer, 'fees_demanded_inr');
  const channels = many(offer, 'agent_channels');
  const transit = many(offer, 'transit_countries');
  const signers = many(offer, 'contract_signatories');
  const contract = one(offer, 'contract_mentioned');
  const fact = (key: string, icon: LucideIcon, field: FieldValue | undefined, value: string | null = field?.value ?? null): Fact => ({ key, icon, field, value });
  return {
    primary: [
      fact('agent', UserRound, agent),
      fact('country', Globe, one(offer, 'destination_country')),
      fact('visa', Contact, visa, visa?.value ? t(`value.visa.${visa.value}`) : null),
      fact('salary', Wallet, salary, salary?.value ? `${cur === 'INR' || !cur ? inr(salary.value) : `${Number(salary.value).toLocaleString('en-IN')} ${cur}`}` : null),
      fact('fee', CircleDollarSign, fee, fee?.value ? inr(fee.value) : null),
      fact('contract', FileText, contract, signers.length ? list(signers) : yn(contract)),
    ],
    more: [
      fact('role', Building2, one(offer, 'role_title'), one(offer, 'role_title')?.value ? tok(one(offer, 'role_title')!.value!) : null),
      fact('employer', Building2, one(offer, 'employer_name')),
      fact('rc', IdCard, one(offer, 'agent_rc_number')),
      fact('payment', Wallet, one(offer, 'fee_payment_mode'), one(offer, 'fee_payment_mode')?.value ? tok(one(offer, 'fee_payment_mode')!.value!) : null),
      fact('channel', MessageCircle, channels[0], channels.length ? list(channels) : null),
      fact('transit', Plane, transit[0], transit.length ? transit.map((c) => c.value).join(', ') : null),
      fact('receipt', Receipt, one(offer, 'receipt_promised'), yn(one(offer, 'receipt_promised'))),
      fact('pbby', HeartPulse, one(offer, 'pbby_insurance_mentioned'), yn(one(offer, 'pbby_insurance_mentioned'))),
      fact('passport', BookUser, one(offer, 'passport_handover_requested'), yn(one(offer, 'passport_handover_requested'))),
    ],
  };
}
