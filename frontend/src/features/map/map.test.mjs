import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { normalizeDistrict } from './districtNames.ts';
import { parseDistrictGeoJSON } from './geoData.ts';
import { SYNTHETIC_MAP_DATA as data } from './syntheticMapData.ts';

const geoText = await readFile(new URL('../../../public/geo/maharashtra-districts.geojson', import.meta.url), 'utf8');
const geo = parseDistrictGeoJSON(JSON.parse(geoText));
const districts = new Set(geo.features.map(feature => normalizeDistrict(feature.properties.district)));

test('renames, casing, and spacing match district boundaries', () => {
  for (const [oldName, newName] of [
    [' Aurangabad ', 'CHHATRAPATI  SAMBHAJINAGAR'],
    ['Ahmednagar', ' Ahilyanagar '], ['Ahmadnagar', 'Ahilyanagar'],
    ['Mumbai', 'Mumbai City'], ['Raigarh', 'Raigad'], ['Bid', 'Beed'],
  ]) assert.equal(normalizeDistrict(oldName), normalizeDistrict(newName));
  assert.notEqual(normalizeDistrict('Mumbai'), normalizeDistrict('Mumbai Suburban'));
});

test('synthetic fixture has only dummy hashes and all districts join', () => {
  assert.equal(data.synthetic, true);
  assert.equal(data.districts.length, 20);
  assert.ok(Number.isFinite(Date.parse(data.generated_at)));
  assert.equal(data.repeated_agents.length, 3);
  assert.equal(data.repeated_templates.length, 2);
  assert.equal(new Set(data.repeated_agents[0].districts.map(normalizeDistrict)).size, 5);
  for (const item of data.districts) {
    assert.ok(districts.has(normalizeDistrict(item.district)), item.district);
    assert.ok(Number.isInteger(item.count) && item.count >= 0);
  }
  const hashes = [];
  for (const item of [...data.repeated_agents, ...data.repeated_templates]) {
    const hash = 'agent_phone_hash' in item ? item.agent_phone_hash : item.offer_template_hash;
    hashes.push(hash);
    assert.match(hash, /^deadbeef[0-9a-f]{56}$/);
    assert.ok(Number.isInteger(item.count) && item.count > 1);
    assert.equal(new Set(item.districts.map(normalizeDistrict)).size, item.districts.length);
    for (const district of item.districts) assert.ok(districts.has(normalizeDistrict(district)), district);
  }
  assert.equal(new Set(hashes).size, 5);
});

test('boundary file covers 36 distinct Maharashtra districts under 1.5 MB', () => {
  assert.equal(geo.features.length, 36);
  assert.equal(districts.size, 36);
  assert.ok(Buffer.byteLength(geoText) < 1_500_000);
  function coordinates(value) {
    if (typeof value[0] === 'number') {
      assert.ok(value[0] >= 72 && value[0] <= 81);
      assert.ok(value[1] >= 15 && value[1] <= 22.2);
    } else value.forEach(coordinates);
  }
  for (const feature of geo.features) coordinates(feature.geometry.coordinates);
});

test('boundary validation rejects malformed and out-of-range geometry', () => {
  for (const invalid of [null, {}, { type: 'FeatureCollection', features: [] },
    { ...geo, features: [{ ...geo.features[0], properties: { district: '' } }] },
    { ...geo, features: [{ ...geo.features[0], geometry: { type: 'Polygon', coordinates: [[[200, 19], [74, 20], [74, 19], [200, 19]]] } }] },
    { ...geo, features: [{ ...geo.features[0], geometry: { type: 'Polygon', coordinates: [[[74, 19], [74, 20], [75, 19], [75, 20]]] } }] },
  ]) assert.throws(() => parseDistrictGeoJSON(invalid));
});
