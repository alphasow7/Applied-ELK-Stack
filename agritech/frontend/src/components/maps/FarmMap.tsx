import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix leaflet default icon
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface FarmMarker {
  id: number
  name: string
  latitude: number
  longitude: number
  region: string
  crop_type?: string
  risk_level?: 'low' | 'medium' | 'high'
  predicted_yield_kg?: number
}

const riskColor = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444' }

export default function FarmMap({ farms }: { farms: FarmMarker[] }) {
  const center: [number, number] = [14.5, -14.5]

  return (
    <MapContainer center={center} zoom={6} style={{ height: '400px', width: '100%', borderRadius: '12px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      {farms.map((farm) => (
        <div key={farm.id}>
          <Marker position={[farm.latitude, farm.longitude]}>
            <Popup>
              <div className="text-sm">
                <strong>{farm.name}</strong>
                <br />Région: {farm.region}
                {farm.crop_type && <><br />Culture: {farm.crop_type}</>}
                {farm.predicted_yield_kg && (
                  <><br />Rendement prévu: {Math.round(farm.predicted_yield_kg).toLocaleString('fr-FR')} kg</>
                )}
                {farm.risk_level && (
                  <><br />Risque: <span style={{ color: riskColor[farm.risk_level] }}>{farm.risk_level}</span></>
                )}
              </div>
            </Popup>
          </Marker>
          {farm.risk_level && (
            <Circle
              center={[farm.latitude, farm.longitude]}
              radius={5000}
              color={riskColor[farm.risk_level]}
              fillOpacity={0.15}
              weight={1}
            />
          )}
        </div>
      ))}
    </MapContainer>
  )
}
