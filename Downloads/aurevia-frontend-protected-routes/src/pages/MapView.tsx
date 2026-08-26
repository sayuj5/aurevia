import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { mockCases, tierMeta } from '../data/mockCases'

export function MapView() {
  const center: [number, number] = [19.5, 76.0]

  return (
    <div className="p-6 md:p-10 h-full flex flex-col">
      <h1 className="font-display text-2xl mb-1">Incident Map</h1>
      <p className="text-sm text-[var(--color-ink-soft)] mb-6">
        Geolocated case density across active districts.
      </p>

      <div className="flex-1 rounded-2xl border border-[var(--color-border)] overflow-hidden min-h-[420px]">
        <MapContainer center={center} zoom={7} style={{ height: '100%', width: '100%' }} scrollWheelZoom={false}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {mockCases.map((c) => (
            <CircleMarker
              key={c.id}
              center={[c.lat, c.lng]}
              radius={10 + c.score / 10}
              pathOptions={{ color: tierMeta[c.tier].color, fillColor: tierMeta[c.tier].color, fillOpacity: 0.6 }}
            >
              <Popup>
                <div className="text-sm">
                  <strong>{c.code}</strong> · {tierMeta[c.tier].label} ({c.score}/100)
                  <br />
                  {c.district}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="flex flex-wrap gap-4 mt-4">
        {(['critical', 'high', 'moderate', 'low'] as const).map((t) => (
          <span key={t} className="flex items-center gap-1.5 text-xs text-[var(--color-ink-soft)]">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: tierMeta[t].color }} />
            {tierMeta[t].label}
          </span>
        ))}
      </div>
    </div>
  )
}
