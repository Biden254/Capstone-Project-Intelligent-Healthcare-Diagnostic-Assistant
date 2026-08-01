import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import {
  isLoggedIn,
  logout,
  me,
  getSymptoms,
  getSamples,
  diagnose,
  getHistory,
} from "../lib/api";

export default function Dashboard() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [symptomOptions, setSymptomOptions] = useState([]);
  const [samples, setSamples] = useState([]);
  const [history, setHistory] = useState([]);

  const [patientId, setPatientId] = useState("");
  const [age, setAge] = useState("");
  const [temperature, setTemperature] = useState("");
  const [heartRate, setHeartRate] = useState("");
  const [bloodPressure, setBloodPressure] = useState("");
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Require auth
  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    me().then(setUser).catch(() => router.push("/login"));
    getSymptoms().then(setSymptomOptions).catch(() => {});
    getSamples().then(setSamples).catch(() => {});
  }, [router]);

  function toggleSymptom(id) {
    setSelectedSymptoms((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  }

  function applySample(index) {
    if (index === "") return;
    const p = samples[index];
    setPatientId(p.patient_id);
    setAge(p.age);
    setTemperature(p.temperature);
    setHeartRate(p.heart_rate);
    setBloodPressure(p.blood_pressure);
    setSelectedSymptoms(p.symptoms.map((s) => s.replace(/ /g, "_")));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const data = await diagnose({
        patient_id: patientId,
        symptoms: selectedSymptoms.map((s) => s.replace(/_/g, " ")),
        age: Number(age),
        temperature: Number(temperature),
        heart_rate: Number(heartRate),
        blood_pressure: bloodPressure,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory() {
    try {
      setHistory(await getHistory());
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <div>
      <header>
        <h1>Healthcare Diagnostic Assistant</h1>
        {user && <p>Logged in as {user.username}</p>}
        <button onClick={handleLogout}>Log out</button>
      </header>

      <section>
        <h2>New patient</h2>
        <form onSubmit={handleSubmit}>
          <div>
            <label>
              Patient ID
              <input value={patientId} onChange={(e) => setPatientId(e.target.value)} />
            </label>
          </div>
          <div>
            <label>
              Age
              <input type="number" value={age} onChange={(e) => setAge(e.target.value)} required />
            </label>
          </div>
          <div>
            <label>
              Temperature (°C)
              <input
                type="number"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
                required
              />
            </label>
          </div>
          <div>
            <label>
              Heart rate (bpm)
              <input
                type="number"
                value={heartRate}
                onChange={(e) => setHeartRate(e.target.value)}
                required
              />
            </label>
          </div>
          <div>
            <label>
              Blood pressure
              <input
                value={bloodPressure}
                onChange={(e) => setBloodPressure(e.target.value)}
                placeholder="120/80"
                required
              />
            </label>
          </div>

          <fieldset>
            <legend>Symptoms</legend>
            {symptomOptions.map((s) => (
              <label key={s.id} style={{ display: "block" }}>
                <input
                  type="checkbox"
                  checked={selectedSymptoms.includes(s.id)}
                  onChange={() => toggleSymptom(s.id)}
                />
                {s.label}
              </label>
            ))}
          </fieldset>

          <div>
            <label>
              Load sample patient:
              <select onChange={(e) => applySample(e.target.value)} defaultValue="">
                <option value="">—</option>
                {samples.map((p, i) => (
                  <option key={p.patient_id} value={i}>
                    {p.patient_id}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Running…" : "Run diagnosis"}
          </button>
        </form>

        {error && <p role="alert">{error}</p>}

        {result && (
          <div>
            <h3>Result</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </section>

      <section>
        <h2>History</h2>
        <button onClick={loadHistory}>Load history</button>
        <ul>
          {history.map((r) => (
            <li key={r.id}>
              {r.patient_id || "(no id)"} — {r.diagnosis} — {r.urgency} —{" "}
              {new Date(r.created_at).toLocaleString()}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
