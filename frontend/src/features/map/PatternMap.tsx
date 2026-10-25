import { useEffect, useId, useMemo, useState } from 'react';
import { geoJSON as leafletGeoJSON } from 'leaflet';
import { GeoJSON, MapContainer, TileLayer, useMap } from 'react-leaflet';
import type { Feature } from 'geojson';
import { normalizeDistrict } from './districtNames';
import { parseDistrictGeoJSON } from './geoData';
import type { DistrictGeoJSON } from './geoData';
import type { MapData } from './types';
import 'leaflet/dist/leaflet.css';
import './map.css';

const defaults: Record<string, string> = {
  title: 'Offer report patterns in Maharashtra',
  syntheticData: 'SYNTHETIC DATA',
  generatedAt: 'Generated at',
  mapLabel: 'Maharashtra offer reports by district',
  loading: 'Loading district boundaries…',
  loadError: 'District boundaries could not be loaded.',
  retry: 'Retry',
  legend: 'Reports per district',
  noData: 'No reports supplied',
  reports: 'reports',
  repeatedAgents: 'Repeated agent phone hashes',
  repeatedTemplates: 'Repeated offer templates',
  hashNote: 'Hashes link reports; repetition alone does not establish wrongdoing.',
  selectAgent: 'Select an agent hash to highlight its districts.',
  selected: 'Highlighted districts',
  clearSelection: 'Clear highlight',
  noAgents: 'No repeated agent hashes.',
  noTemplates: 'No repeated templates.',
  districtCounts: 'District report counts',
  boundaryNote: 'District boundaries: 2021 source, simplified for this prototype.',
};

const bins = [
  { min: 0, label: '0', color: '#f0f4f8' },
  { min: 1, label: '1–10', color: '#b9dfdf' },
  { min: 11, label: '11–25', color: '#70b8bd' },
  { min: 26, label: '26–50', color: '#30858f' },
  { min: 51, label: '51+', color: '#15515e' },
];
const noDataColor = '#e5e7eb';
const fillColor = (count: number | undefined) => count === undefined ? noDataColor
  : bins.reduce((color, bin) => count >= bin.min ? bin.color : color, bins[0].color);
const shortHash = (hash: string) => hash.slice(0, 12) + '…' + hash.slice(-6);

function MapViewport({ geo }: { geo: DistrictGeoJSON | null }) {
  const map = useMap();
  useEffect(() => {
    if (geo) map.fitBounds(leafletGeoJSON(geo).getBounds(), { padding: [16, 16] });
  }, [geo, map]);
  useEffect(() => {
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(map.getContainer());
    return () => observer.disconnect();
  }, [map]);
  return null;
}

export function PatternMap({ data, labels }: { data: MapData; labels?: Partial<Record<string, string>> }) {
  const t = { ...defaults };
  for (const [key, value] of Object.entries(labels ?? {})) {
    if (value !== undefined) t[key] = value;
  }
  const headingId = useId();
  const [geo, setGeo] = useState<DistrictGeoJSON | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [selectedHash, setSelectedHash] = useState<string | null>(null);
  const selectedAgent = data.repeated_agents.find(agent => agent.agent_phone_hash === selectedHash);
  const highlighted = new Set(selectedAgent?.districts.map(normalizeDistrict));
  const counts = useMemo(() => {
    const result = new Map<string, number>();
    for (const item of data.districts) {
      const name = normalizeDistrict(item.district);
      result.set(name, (result.get(name) ?? 0) + item.count);
    }
    return result;
  }, [data.districts]);

  useEffect(() => {
    const controller = new AbortController();
    setFailed(false);
    fetch('/geo/maharashtra-districts.geojson', { signal: controller.signal })
      .then(response => {
        if (!response.ok) throw new Error('Boundary request failed');
        return response.json() as Promise<unknown>;
      })
      .then(value => { if (!controller.signal.aborted) setGeo(parseDistrictGeoJSON(value)); })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, [attempt]);

  const districtCount = (feature: Feature) => counts.get(normalizeDistrict(String(feature.properties?.district ?? '')));
  const boundaryAttribution = 'District boundaries: <a href="https://www.geoboundaries.org/">geoBoundaries</a> / Pathways Data, '
    + '<a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a> (simplified)';

  return (
    <section className="pattern-map" aria-labelledby={headingId}>
      <header className="pattern-map__header">
        <h2 id={headingId}>{t.title}</h2>
        {data.synthetic && <strong className="pattern-map__badge">{t.syntheticData}</strong>}
        <p>{t.generatedAt}: <time dateTime={data.generated_at}>{data.generated_at}</time></p>
      </header>
      <div className="pattern-map__layout">
        <div className="pattern-map__visual">
          <div className="pattern-map__canvas" role="region" aria-label={t.mapLabel}>
            <MapContainer center={[19, 76.5]} zoom={6} minZoom={5} scrollWheelZoom={false}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution={'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}
                maxZoom={19}
                referrerPolicy="strict-origin-when-cross-origin"
              />
              <MapViewport geo={geo} />
              {geo && <GeoJSON
                key={JSON.stringify([data.districts, t.reports, t.noData])}
                data={geo}
                attribution={boundaryAttribution}
                style={feature => {
                  const active = highlighted.has(normalizeDistrict(String(feature?.properties?.district ?? '')));
                  return {
                    fillColor: feature ? fillColor(districtCount(feature)) : noDataColor,
                    fillOpacity: selectedAgent && !active ? 0.3 : 0.8,
                    color: active ? '#9a3412' : '#ffffff',
                    weight: active ? 3 : 1,
                    opacity: 1,
                  };
                }}
                onEachFeature={(feature, layer) => {
                  const tooltip = document.createElement('span');
                  const count = districtCount(feature);
                  tooltip.textContent = String(feature.properties?.district) + ': '
                    + (count === undefined ? t.noData : count + ' ' + t.reports);
                  layer.bindTooltip(tooltip, { sticky: true });
                }}
              />}
            </MapContainer>
          </div>
          {!geo && <div className="pattern-map__status" role={failed ? 'alert' : 'status'}>
            <span>{failed ? t.loadError : t.loading}</span>
            {failed && <button type="button" onClick={() => setAttempt(value => value + 1)}>{t.retry}</button>}
          </div>}
          <div className="pattern-map__legend" aria-label={t.legend}>
            <strong>{t.legend}</strong>
            <ul>
              <li><i style={{ backgroundColor: noDataColor }} aria-hidden="true" />{t.noData}</li>
              {bins.map(bin => <li key={bin.min}><i style={{ backgroundColor: bin.color }} aria-hidden="true" />{bin.label}</li>)}
            </ul>
          </div>
          <p className="pattern-map__note">{t.boundaryNote}</p>
          <details className="pattern-map__counts">
            <summary>{t.districtCounts}</summary>
            <ul>{data.districts.map((item, index) => <li key={index}>{item.district}: {item.count} {t.reports}</li>)}</ul>
          </details>
        </div>
        <aside className="pattern-map__panel" aria-label={t.repeatedAgents}>
          <h3>{t.repeatedAgents}</h3>
          <p>{t.hashNote}</p>
          <p>{t.selectAgent}</p>
          {data.repeated_agents.length === 0 && <p>{t.noAgents}</p>}
          <ul className="pattern-map__items">
            {data.repeated_agents.map(agent => <li key={agent.agent_phone_hash}>
              <button type="button" aria-pressed={agent.agent_phone_hash === selectedAgent?.agent_phone_hash}
                onClick={() => setSelectedHash(agent.agent_phone_hash === selectedHash ? null : agent.agent_phone_hash)}>
                <code title={agent.agent_phone_hash}>{shortHash(agent.agent_phone_hash)}</code>
                <span>{agent.count} {t.reports}</span>
                <span>{agent.districts.join(', ')}</span>
              </button>
            </li>)}
          </ul>
          <div className="pattern-map__selection" role="status">
            {selectedAgent && <>
              <p>{t.selected}: {selectedAgent.districts.join(', ')}</p>
              <button type="button" onClick={() => setSelectedHash(null)}>{t.clearSelection}</button>
            </>}
          </div>
          <h3>{t.repeatedTemplates}</h3>
          {data.repeated_templates.length === 0 && <p>{t.noTemplates}</p>}
          <ul className="pattern-map__items pattern-map__templates">
            {data.repeated_templates.map(template => <li key={template.offer_template_hash}>
              <code title={template.offer_template_hash}>{shortHash(template.offer_template_hash)}</code>
              <span>{template.count} {t.reports}</span>
              <span>{template.districts.join(', ')}</span>
            </li>)}
          </ul>
        </aside>
      </div>
    </section>
  );
}
