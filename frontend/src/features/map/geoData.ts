import type { FeatureCollection, MultiPolygon, Polygon } from 'geojson';

export type DistrictGeoJSON = FeatureCollection<Polygon | MultiPolygon, { district: string }>;

function ring(value: unknown): boolean {
  if (!Array.isArray(value) || value.length < 4) return false;
  const valid = value.every(point => Array.isArray(point) && point.length >= 2
    && Number.isFinite(point[0]) && Number.isFinite(point[1])
    && Math.abs(point[0]) <= 180 && Math.abs(point[1]) <= 90);
  const first = value[0];
  const last = value[value.length - 1];
  return valid && first[0] === last[0] && first[1] === last[1];
}

function polygon(value: unknown): boolean {
  return Array.isArray(value) && value.length > 0 && value.every(ring);
}

export function parseDistrictGeoJSON(value: unknown): DistrictGeoJSON {
  if (!value || typeof value !== 'object' || !('type' in value)
    || value.type !== 'FeatureCollection' || !('features' in value)
    || !Array.isArray(value.features) || value.features.length === 0
    || !value.features.every(feature => feature?.type === 'Feature'
      && typeof feature.properties?.district === 'string' && feature.properties.district.trim()
      && (feature.geometry?.type === 'Polygon' ? polygon(feature.geometry.coordinates)
        : feature.geometry?.type === 'MultiPolygon'
          && Array.isArray(feature.geometry.coordinates) && feature.geometry.coordinates.length > 0
          && feature.geometry.coordinates.every(polygon)))) {
    throw new Error('Invalid district boundary data');
  }
  return value as DistrictGeoJSON;
}
