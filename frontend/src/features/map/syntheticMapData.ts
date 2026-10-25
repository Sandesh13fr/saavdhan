import type { MapData } from './types';

// Deliberate dummy hex strings, never derived from phone numbers or documents.
export const SYNTHETIC_MAP_DATA: MapData = {
  synthetic: true,
  generated_at: '2026-10-25T00:00:00Z',
  districts: [
    { district: 'Pune', count: 84 },
    { district: 'Mumbai', count: 68 },
    { district: 'Thane', count: 61 },
    { district: 'Nagpur', count: 47 },
    { district: 'Nashik', count: 42 },
    { district: 'Chhatrapati Sambhajinagar', count: 36 },
    { district: 'Kolhapur', count: 25 },
    { district: 'Solapur', count: 32 },
    { district: 'Satara', count: 19 },
    { district: 'Sangli', count: 23 },
    { district: 'Ahmednagar', count: 31 },
    { district: 'Jalgaon', count: 27 },
    { district: 'Latur', count: 18 },
    { district: 'Nanded', count: 29 },
    { district: 'Amravati', count: 21 },
    { district: 'Akola', count: 16 },
    { district: 'Ratnagiri', count: 12 },
    { district: 'Raigad', count: 24 },
    { district: 'Palghar', count: 33 },
    { district: 'Beed', count: 22 },
  ],
  repeated_agents: [
    { agent_phone_hash: 'deadbeef' + '0'.repeat(56), count: 18,
      districts: ['Pune', 'Thane', 'Nashik', 'Aurangabad', 'Ahmednagar'] },
    { agent_phone_hash: 'deadbeef' + '1'.repeat(56), count: 9,
      districts: ['Nagpur', 'Amravati', 'Akola'] },
    { agent_phone_hash: 'deadbeef' + '2'.repeat(56), count: 7,
      districts: ['Mumbai', 'Raigad', 'Palghar'] },
  ],
  repeated_templates: [
    { offer_template_hash: 'deadbeef' + 'a'.repeat(56), count: 24,
      districts: ['Pune', 'Solapur', 'Satara', 'Sangli'] },
    { offer_template_hash: 'deadbeef' + 'b'.repeat(56), count: 16,
      districts: ['Latur', 'Nanded', 'Beed'] },
  ],
};
