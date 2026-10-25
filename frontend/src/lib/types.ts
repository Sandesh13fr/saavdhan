export type Lang = 'en' | 'hi' | 'mr';
export type Level = 'STOP' | 'VERIFY_FIRST' | 'NO_RED_FLAGS_FOUND';
export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type Status = 'hit' | 'clear' | 'unknown';

export interface FieldValue { value: string | null; quote: string; source_ref: string | null; confidence?: string | null }
export type Offer = { source_ids?: string[] } & Record<string, FieldValue | FieldValue[] | string[] | undefined>;

export interface RuleHit {
  rule_id: string; severity: Severity; status: Status; evidence: FieldValue[];
  explanation_key: string; rule_source_url: string; heuristic: boolean;
}
export interface Verdict { level: Level; rule_hits: RuleHit[]; ra_list_date: string; next_steps_key: string }
export interface Analysis { offer: Offer; verdict: Verdict; extraction_method: 'llm' | 'fallback'; errors: string[] }

export interface Contact { alias: string; channel: string }
export interface SafetyPlan { traveller_alias: string; contacts: Contact[]; itinerary: string[]; checkin_interval_hours: number }
export interface Alert { to_alias: string; channel: string; at: string; message_key: string; simulated: boolean }
export interface Safety {
  plan: SafetyPlan; checkins: { at: string; note: string }[];
  status: 'ok' | 'due' | 'missed'; next_due: string; now: string; alerts: Alert[];
}
export interface CaseView {
  id: string; created_at: string; demo: boolean; revision: number;
  sources: Record<string, unknown>[]; audit: unknown[]; analysis: Analysis | null; safety: Safety | null;
}
export interface Meta {
  app: string; version: string; ra_list_date: string; fee_cap_inr: number;
  rules: { id: string; severity: Severity; source: string; heuristic: boolean }[];
}
