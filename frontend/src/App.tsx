import { useEffect, useState } from "react";
import { api, HealthResponse, Skill } from "./api/client";
import { SkillsDashboard, ValidationPage } from "./components";

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [catalogSkills, setCatalogSkills] = useState<Array<{ id: string; name: string; category: string }>>([]);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const data = await api.health();
        setHealth(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to connect");
      } finally {
        setLoading(false);
      }
    }
    fetchHealth();
  }, []);

  useEffect(() => {
    async function fetchCatalogSummary() {
      try {
        const data = await api.listSkills({ page_size: 1000 });
        setCatalogSkills(data.items.map((s: Skill) => ({ id: s.id, name: s.name, category: s.category })));
      } catch {
        // Silently fail - validation page will handle empty catalog
      }
    }
    fetchCatalogSummary();
  }, []);

  return (
    <div className="container" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>
      <header style={{ marginBottom: "2rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "2.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
          Sentinel Station
        </h1>
        <p style={{ color: "var(--color-text-muted)", fontSize: "1.125rem" }}>
          Local agent-first control plane for AI/ML skills catalog, validation, and planning.
        </p>
        <p style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
          Alan Vo | AI & Machine Learning
        </p>
      </header>

      <main>
        <section className="card" style={{ marginBottom: "2rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem" }}>
            <h2 style={{ fontSize: "1.25rem" }}>System Health</h2>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
              {loading && <div className="loading">Checking backend connection…</div>}
              {error && <div className="error">{error}</div>}
              {health && (
                <>
                  <span className="badge badge-success">{health.status}</span>
                  <span style={{ color: "var(--color-text-muted)" }}>{health.service}</span>
                  <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                    API: <code>/api/v1/health</code>
                  </span>
                </>
              )}
            </div>
          </div>

          <div style={{ paddingTop: "1rem", borderTop: "1px solid var(--color-border)" }}>
            <h3 style={{ marginBottom: "0.75rem", fontSize: "1rem" }}>Available Endpoints</h3>
            <ul style={{ display: "grid", gap: "0.5rem", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
              <li><code>GET /api/v1/health</code> — Service health check</li>
              <li><code>GET /api/v1/skills</code> — List skills with pagination & filters</li>
              <li><code>GET /api/v1/skills/:id</code> — Skill detail</li>
              <li><code>POST /api/v1/validate</code> — Validate skill stack compatibility</li>
              <li><code>POST /api/v1/plan</code> — Generate execution plan</li>
              <li><code>POST /api/v1/plan/export</code> — Export plan as JSON/Markdown</li>
              <li><code>GET /docs</code> — OpenAPI documentation</li>
            </ul>
          </div>
        </section>

        <SkillsDashboard />
        <ValidationPage catalogSkills={catalogSkills} />
      </main>

      <footer style={{ marginTop: "3rem", textAlign: "center", color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
        <p>Sentinel Station v1.0.0 — <a href="https://github.com/ALANDVO/sentinel-station-alan-vo" target="_blank" rel="noopener">GitHub</a></p>
      </footer>
    </div>
  );
}

export default App;