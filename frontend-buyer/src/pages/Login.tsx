import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { apiFetch, setTokens } from "@/api/client";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const res = await apiFetch<{ access_token: string; refresh_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      setTokens(res.access_token, res.refresh_token);
      navigate("/");
    } catch (err) { setError(err instanceof Error ? err.message : "Login failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-blue-600 mb-1">E-Commerce Platform</h1>
          <p className="text-gray-500">Sign in to your account</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>}
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required className="w-full h-11 px-4 rounded-xl border border-gray-200 text-sm" />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required className="w-full h-11 px-4 rounded-xl border border-gray-200 text-sm" />
          <button type="submit" disabled={loading} className="w-full h-11 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2">
            {loading && <Loader2 className="h-4 w-4 animate-spin" />} Sign in
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">No account? <Link to="/register" className="text-blue-600 hover:underline">Sign up</Link></p>
      </div>
    </div>
  );
}
