# Third-party map assets and dependencies

Retrieved and verified: 2026-10-25. This prototype uses synthetic report counts and dummy hashes only. The geographic boundaries and base map are public geographic data.

## Maharashtra district boundaries

- Local asset: `frontend/public/geo/maharashtra-districts.geojson`.
- Source: [geoBoundaries gbOpen India ADM2 API](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM2/).
- Pinned source file: https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/9469f09/releaseData/gbOpen/IND/ADM2/geoBoundaries-IND-ADM2_simplified.geojson
- Boundary ID: `IND-ADM2-76128533`; represented year: 2021; upstream sources: Pathways Data Pvt. Ltd. and lgdirectory.gov.in; upstream build: 2023-12-12.
- License: [Open Data Commons Open Database License 1.0 (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/). The derived district-boundary database remains available under ODbL 1.0. No application code or report data is included in this boundary database.
- Attribution displayed on the map: District boundaries: geoBoundaries / Pathways Data, ODbL 1.0 (simplified).
- Size: **438,351 bytes** (about 428 KiB); **36 features**, including Mumbai City, Mumbai Suburban and Palghar.
- Processing: used the upstream simplified GeoJSON (7,979,916 bytes), selected the 36 Maharashtra district names, and required every coordinate to lie within longitude 72–81 / latitude 15–22.2 to disambiguate Aurangabad in Bihar and Raigarh in Chhattisgarh. Kept the original simplified polygon coordinates and WGS84 longitude/latitude order. Removed upstream metadata and CRS members, compacted JSON, and retained only a normalized `district` property per feature. No additional coordinate simplification was needed.
- Property renames: Ahmadnagar → Ahilyanagar; Aurangabad → Chhatrapati Sambhajinagar; Bid → Beed; Buldana → Buldhana; Gondiya → Gondia; Raigarh → Raigad; Osmanabad → Dharashiv; Mumbai → Mumbai City. Display-name modernization does not update the 2021 boundary geometry.
- These are simplified prototype boundaries, not a current official administrative boundary certification. The source API documents the upstream license and provenance. Retain this notice and the ODbL link when redistributing the asset.

## Packages

These dependencies implement the requested interactive map; no CSS framework or API-key service was added. Versions below are the recorded lockfile versions, compatible with the app's React 19 peer dependencies.

| Package | Version | License | Source / license |
| --- | --- | --- | --- |
| leaflet | 1.9.4 | BSD-2-Clause | https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE |
| react-leaflet | 5.0.0 | Hippocratic-2.1 | https://github.com/PaulLeCam/react-leaflet/blob/v5.0.0/LICENSE.md |
| @react-leaflet/core (transitive) | 3.0.0 | Hippocratic-2.1 | https://github.com/PaulLeCam/react-leaflet/blob/v5.0.0/LICENSE.md |
| @types/leaflet (development) | 1.9.21 | MIT | https://www.npmjs.com/package/@types/leaflet |
| @types/geojson (transitive development) | 7946.0.16 | MIT | https://www.npmjs.com/package/@types/geojson |

Package versions, integrity hashes and peer dependencies were checked against their version-specific registry.npmjs.org metadata. React Leaflet 5 requires React / React DOM ^19.0.0 and Leaflet ^1.9.0.

## OpenStreetMap base map

- Requested tile URL: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`; Leaflet uses subdomains a, b and c.
- Attribution displayed on the map: © OpenStreetMap contributors, linked to https://www.openstreetmap.org/copyright.
- Geographic database: [ODbL 1.0](https://www.openstreetmap.org/copyright). Standard raster tiles are an ODbL Produced Work requiring attribution, as documented in the [OSMF licensing FAQ, section 1.6](https://osmfoundation.org/wiki/Licence/Licence_and_Legal_FAQ). The historical CC BY-SA tile license is no longer the current tile license.
- Tile-service conditions: https://operations.osmfoundation.org/policies/tiles/. No API key is needed. Normal browser cache behavior is retained; no bulk download or prefetch feature is implemented.
- The current tile policy documents the canonical non-subdomain endpoint `https://tile.openstreetmap.org/{z}/{x}/{y}.png` and warns other subdomains may be withdrawn. This feature retains the task's explicit subdomain URL; review the endpoint before production use.
- Tile requests disclose the viewer's IP address, browser headers and viewed map area to the OSM tile service. They do not include report counts, district selections, hashes or documents.

## Lead integration: CSP and referrer

Do not edit the backend from the map lane. In `backend/main.py`, replace the current image directive with exactly:

```text
img-src 'self' data: https://a.tile.openstreetmap.org https://b.tile.openstreetmap.org https://c.tile.openstreetmap.org;
```

Keep `connect-src 'self'`: the GeoJSON fetch is same-origin and Leaflet loads tiles through image elements. No external script, font or CSS host is needed. If the lead adopts the canonical tile endpoint instead, use `https://tile.openstreetmap.org` in `img-src` and update the URL together.

The backend currently sends `Referrer-Policy: no-referrer`. The TileLayer explicitly sets `referrerPolicy="strict-origin-when-cross-origin"` on its images so the tile service receives the origin Referer required by its policy. A global backend referrer-policy change is not needed for this component.

The lead must mount the feature behind the authority login. This lane owns no authentication or application routing.
