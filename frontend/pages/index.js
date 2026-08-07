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

const URGENCY_STYLES = {
  LOW: "bg-green text-bg-dark",
  MEDIUM: "bg-yellow text-bg-dark",
  HIGH: "bg-orange text-bg-dark",
  CRITICAL: "bg-red text-bg-dark",
};

export default function Dashboard() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [symptomOptions, setSymptomOptions] = useState([]);
  const [samples, setSamples] = useState([]);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const [patientId, setPatientId] = useState("");
  const [age, setAge] = useState("");
  const [temperature, setTemperature] = useState("");
  const [heartRate, setHeartRate] = useState("");
  const [bloodPressure, setBloodPressure] = useState("");
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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
      setShowHistory(true);
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-bg-dark p-4 md:p-8">
      <div className="max-w-6xl mx-auto rounded-lg border border-border bg-bg shadow-2xl overflow-hidden">
        {/* titlebar */}
        <div className="flex items-center gap-3 px-4 py-3 bg-bg-dark border-b border-border">
          <span className="flex-1 text-center text-xs text-fg-dim">
            agent.py — patient intake — healthcare-diagnostic-assistant
          </span>
          {user && (
            <div className="flex items-center gap-3 text-xs text-fg-dim">
              <span>{user.username}</span>
              <button
                onClick={handleLogout}
                className="rounded border border-border-lit px-2 py-1 hover:border-red hover:text-red transition-colors"
              >
                log out
              </button>
            </div>
          )}
        </div>

        {/* two-pane layout */}
        <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border min-h-[560px]">
          {/* LEFT: intake form */}
          <section className="bg-panel p-5">
            <p className="text-cyan text-xs mb-4">─ intake ──────────────────────────</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs text-fg-dim mb-1"># patient_id</label>
                <input
                  className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                  placeholder="P001"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-fg-dim mb-1"># age</label>
                  <input
                    type="number"
                    className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                    placeholder="34"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-fg-dim mb-1"># temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                    placeholder="38.9"
                    value={temperature}
                    onChange={(e) => setTemperature(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-fg-dim mb-1"># heart_rate</label>
                  <input
                    type="number"
                    className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                    placeholder="98"
                    value={heartRate}
                    onChange={(e) => setHeartRate(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-fg-dim mb-1"># blood_pressure</label>
                  <input
                    className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                    placeholder="120/80"
                    value={bloodPressure}
                    onChange={(e) => setBloodPressure(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-fg-dim mb-2"># symptoms[] — click to toggle</label>
                <div className="flex flex-wrap gap-1.5">
                  {symptomOptions.length === 0 && (
                    <span className="text-xs text-fg-dimmer">loading symptom vocabulary…</span>
                  )}
                  {symptomOptions.map((s) => {
                    const active = selectedSymptoms.includes(s.id);
                    return (
                      <button
                        type="button"
                        key={s.id}
                        onClick={() => toggleSymptom(s.id)}
                        className={`rounded-full px-3 py-1 text-xs border transition-colors ${
                          active
                            ? "bg-purple border-purple text-bg-dark font-semibold"
                            : "bg-input border-border-lit text-fg-dim hover:border-blue hover:text-fg"
                        }`}
                      >
                        {s.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-md bg-green text-bg-dark font-semibold text-sm px-4 py-2 hover:brightness-110 disabled:opacity-50 transition"
                >
                  {loading ? "Running…" : "▶ run diagnosis"}
                </button>
                <select
                  onChange={(e) => applySample(e.target.value)}
                  defaultValue=""
                  className="rounded-md border border-border-lit bg-input px-2 py-2 text-xs text-fg outline-none"
                >
                  <option value="">— load sample patient —</option>
                  {samples.map((p, i) => (
                    <option key={p.patient_id} value={i}>
                      {p.patient_id}
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <p className="text-xs text-red border border-red/30 bg-red/10 rounded-md px-3 py-2">
                  {error}
                </p>
              )}
            </form>
          </section>

          {/* RIGHT: output */}
          <section className="bg-panel p-5">
            <p className="text-cyan text-xs mb-4">─ diagnosis ───────────────────────</p>

            {!result && !loading && (
              <>
                <p className="text-xs text-fg-dim leading-relaxed">
                  Fill in the intake form and run a diagnosis to see the agent&apos;s
                  Perceive → Think → Act cycle here: per-module confidence, aggregate
                  diagnosis, urgency, and the generated treatment plan.
                </p>
              </>
            )}

            {loading && (
              <p className="text-xs text-fg-dim">perceive → think → act …</p>
            )}

            {result && (
              <div> 
                {/*<p className="text-xs mb-4">
                  <span className="text-green">agent</span>
                  <span className="text-fg-dim">:~$</span> ./run_diagnosis.sh --patient{" "}
                  {result.report.patient_id}
                </p>*/}

                <div className="space-y-1.5 mb-5">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue text-bg-dark">
                      DIAGNOSIS
                    </span>
                    <span>{result.report.diagnosis}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-fg-dimmer text-fg">
                      CONFIDENCE
                    </span>
                    <span>{(result.report.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        URGENCY_STYLES[result.report.urgency] || URGENCY_STYLES.MEDIUM
                      }`}
                    >
                      {result.report.urgency}
                    </span>
                    <span>next action: {result.report.next_action}</span>
                  </div>
                </div>

                <p className="text-purple text-xs mb-2"># recommendations</p>
                <ul className="text-sm space-y-1 mb-5">
                  {result.report.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>

                <p className="text-purple text-xs mb-2"># module breakdown</p>
                <table className="w-full text-xs mb-5">
                  <thead>
                    <tr className="text-fg-dim">
                      <th className="text-left font-normal pb-1">module</th>
                      <th className="text-left font-normal pb-1">diagnosis</th>
                      <th className="text-left font-normal pb-1">confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.module_breakdown).map(([name, m]) => (
                      <tr key={name} className="border-t border-border">
                        <td className="py-1.5">{name}</td>
                        <td className="py-1.5">{m.diagnosis ?? "—"}</td>
                        <td className="py-1.5 text-cyan">
                          {m.confidence != null ? (m.confidence * 100).toFixed(1) + "%" : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <p className="text-purple text-xs mb-2">
                  # treatment plan ({result.treatment_plan.steps ?? 0} steps)
                </p>
                <ul className="text-xs space-y-1.5">
                  {(result.treatment_plan.plan || []).map((s) => (
                    <li
                      key={s.step}
                      className="flex gap-2 pb-1.5 border-b border-dashed border-border last:border-none"
                    >
                      <span className="text-cyan w-5 flex-shrink-0">{s.step}.</span>
                      <span className="flex-1">{s.action}</span>
                      <span className="text-fg-dim">[{s.duration}]</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </div>

        {/* status bar */}
        <div className="flex items-center gap-3 px-4 py-2 bg-bg-dark border-t border-border text-[11px] text-fg-dim">
          <button onClick={loadHistory} className="hover:text-fg transition-colors">
            <span className="rounded bg-input px-1.5 py-0.5 text-fg font-semibold mr-1">
              history
            </span>
            load past diagnoses
          </button>
          <span className="text-border-lit">│</span>
          <span className="ml-auto">
            {symptomOptions.length > 0 ? `${symptomOptions.length} symptoms loaded` : "connecting…"}
          </span>
        </div>

        {showHistory && (
          <div className="border-t border-border bg-panel p-5">
            <p className="text-purple text-xs mb-3"># history</p>
            {history.length === 0 ? (
              <p className="text-xs text-fg-dim">No diagnoses yet.</p>
            ) : (
              <ul className="text-xs space-y-1.5">
                {history.map((r) => (
                  <li key={r.id} className="flex gap-3">
                    <span className="text-fg-dim w-32 flex-shrink-0">
                      {new Date(r.created_at).toLocaleString()}
                    </span>
                    <span className="w-20 flex-shrink-0">{r.patient_id || "(no id)"}</span>
                    <span className="flex-1">{r.diagnosis}</span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded self-start ${
                        URGENCY_STYLES[r.urgency] || URGENCY_STYLES.MEDIUM
                      }`}
                    >
                      {r.urgency}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
