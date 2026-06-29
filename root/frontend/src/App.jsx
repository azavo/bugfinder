import {useState} from 'react'

function App() {
  const [lat, setLat] = useState(40.47)
  const [lon, setLon] = useState(-74.7)
  const [datetimeStr, setDatetimeStr] = useState('')
  const [inatusername, setInatUsername] = useState('')
  const [unseen, setUnseen] = useState(false)
  const mode = unseen ? "unseen" : "all"

  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)


  return (
    <div>
      <h1>BUGFINDER</h1>

      <label>
        Latitude:
        <input
          type="number"
          value={lat}
          onChange={(e) => setLat(e.target.value)}
        />
      </label>

      <label>
        Longitude:
        <input
          type="number"
          value={lon}
          onChange={(e) => setLon(e.target.value)}
        />
      </label>
      <label>
        Date & Time:
        <input
          type="datetime-local"
          value={datetimeStr}
          onChange={(e) => setDatetimeStr(e.target.value)}
        />
      </label>

      <label>
        iNaturalist Username:
        <input
          type="text"
          value={inatusername}
          onChange={(e) => setInatUsername(e.target.value)}
        />
      </label>
      <label>
        Unseen:
        <input
          type="checkbox"
          checked={unseen}
          onChange={(e) => setUnseen(e.target.checked)}
        />
      </label>

      <p>You entered: {lat}, {lon}, {datetimeStr}, {inatusername}, {mode}</p>
      <button onClick={handleSubmit}>Find Bugs</button>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {predictions && <pre>{JSON.stringify(predictions, null, 2)}</pre>}
      
    </div>
    
  )


  async function handleSubmit() {
    setLoading(true)
    setError(null)

    const params = new URLSearchParams({
      lat,
      lon,
      datetime_str: datetimeStr,
      inat_username: inatusername,
      mode,
    })

    try {
      const response = await fetch(`http://127.0.0.1:8000/predict?${params}`)
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }
      const data = await response.json()
      setPredictions(data.predictions)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
}



export default App
