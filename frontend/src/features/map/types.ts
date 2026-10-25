export type MapData = {
  synthetic: boolean;
  generated_at: string;
  districts: { district: string; count: number }[];
  repeated_agents: { agent_phone_hash: string; districts: string[]; count: number }[];
  repeated_templates: { offer_template_hash: string; districts: string[]; count: number }[];
};
