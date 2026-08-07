import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { register } from "../lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ username, email, password });
      router.push("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-dark p-6">
      <div className="w-full max-w-md rounded-lg border border-border bg-panel shadow-2xl overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3 bg-bg-dark border-b border-border">
          <span className="text-xs text-fg-dim">register</span>
        </div>

        <div className="p-8">
          <h1 className="text-lg font-semibold text-fg mb-6">Create an account</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-fg-dim mb-1"># username</label>
              <input
                className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs text-fg-dim mb-1"># email (optional)</label>
              <input
                type="email"
                className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs text-fg-dim mb-1"># password (min 8 chars)</label>
              <input
                type="password"
                className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm text-fg outline-none focus:border-blue transition-colors"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>

            {error && (
              <p className="text-xs text-red border border-red/30 bg-red/10 rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-green text-bg-dark font-semibold text-sm py-2.5 hover:brightness-110 disabled:opacity-50 transition"
            >
              {loading ? "Creating account…" : "▶ Register"}
            </button>
          </form>

          <p className="text-xs text-fg-dim mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-cyan hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
