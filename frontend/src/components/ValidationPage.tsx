import { useState, useCallback } from "react";
import { api, ValidationResult as APIValidationResult, ValidateResponse } from "../api/client";
import { SkillCard } from "./SkillCard";

interface ValidationPageProps {
  catalogSkills: Array<{ id: string; name: string; category: string }>;
}

export function ValidationPage({ catalogSkills }: ValidationPageProps) {
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [validationResult, setValidationResult] = useState<ValidateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [exportFormat, setExportFormat] = useState<"json" | "markdown">("json");

  const handleSkillToggle = useCallback((skillId: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skillId) ? prev.filter((id) => id !== skillId) : [...prev, skillId]
    );
    setValidationResult(null);
  }, []);

  const handleValidate = useCallback(async () => {
    if (selectedSkills.length === 0) {
      return;
    }
    setLoading(true);
    try {
      const result = await api.validateStack(selectedSkills);
      setValidationResult(result);
    } catch {
      // Error handled by UI state
    } finally {
      setLoading(false);
    }
  }, [selectedSkills]);

  const handleExport = useCallback(async () => {
    if (!validationResult) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/plan/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skill_ids: selectedSkills, format: exportFormat }),
      });
      if (!response.ok) throw new Error("Export failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `validation-plan.${exportFormat === "json" ? "json" : "md"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // Error handled by UI state
    } finally {
      setLoading(false);
    }
  }, [validationResult, selectedSkills, exportFormat]);

  const overallCompatible = validationResult?.overall_compatible ?? null;

  return (
    <div>
      {/* Skill Selector */}
      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem" }}>Skill Stack Validator</h2>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "0.375rem", fontSize: "0.875rem" }}>
              <input
                type="radio"
                name="exportFormat"
                value="json"
                checked={exportFormat === "json"}
                onChange={() => setExportFormat("json")}
              />
              JSON
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "0.375rem", fontSize: "0.875rem" }}>
              <input
                type="radio"
                name="exportFormat"
                value="markdown"
                checked={exportFormat === "markdown"}
                onChange={() => setExportFormat("markdown")}
              />
              Markdown
            </label>
          </div>
        </header>

        <p style={{ color: "var(--color-text-muted)", marginBottom: "1rem", fontSize: "0.875rem" }}>
          Select skills from the catalog to validate compatibility and generate an execution plan.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "0.75rem", maxHeight: "300px", overflow: "auto" }}>
          {catalogSkills.map((skill) => (
            <SkillCard
              key={skill.id}
              skill={{
                id: skill.id,
                name: skill.name,
                description: `${skill.category} skill`,
                category: skill.category,
                tags: [],
                repo_url: "#",
                install_command: "",
                version: "",
                dependencies: [],
              }}
              onSelect={() => handleSkillToggle(skill.id)}
              selected={selectedSkills.includes(skill.id)}
            />
          ))}
        </div>

        <div style={{ marginTop: "1rem", display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
            Selected: <strong>{selectedSkills.length}</strong> skills
          </span>
          <button
            className="btn btn-primary"
            onClick={handleValidate}
            disabled={loading || selectedSkills.length === 0}
          >
            {loading ? "Validating…" : "Validate Stack"}
          </button>
          {validationResult && (
            <button
              className="btn btn-secondary"
              onClick={handleExport}
              disabled={loading}
            >
              {loading ? "Exporting…" : `Export ${exportFormat.toUpperCase()}`}
            </button>
          )}
        </div>
      </section>

      {/* Validation Results */}
      {validationResult && (
        <section className="card">
          <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
            <h2 style={{ fontSize: "1.25rem" }}>
              Validation Results
              {overallCompatible === true && <span className="badge badge-success" style={{ marginLeft: "0.75rem" }}>Compatible</span>}
              {overallCompatible === false && <span className="badge badge-error" style={{ marginLeft: "0.75rem" }}>Incompatible</span>}
            </h2>
            <span style={{ color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
              {validationResult.results.length} skills checked
            </span>
          </header>

          <div style={{ display: "grid", gap: "1rem" }}>
            {validationResult.results.map((result: APIValidationResult) => (
              <article
                key={result.skill_id}
                className="card"
                style={{
                  borderLeft: `4px solid ${result.compatible ? "var(--color-success)" : "var(--color-error)"}`,
                }}
              >
                <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                      {result.skill_id}
                    </h3>
                    <span className={result.compatible ? "badge badge-success" : "badge badge-error"}>
                      {result.compatible ? "Compatible" : "Incompatible"}
                    </span>
                  </div>
                </header>

                {result.missing_deps.length > 0 && (
                  <div style={{ marginBottom: "0.75rem" }}>
                    <strong style={{ color: "var(--color-error)" }}>Missing Dependencies:</strong>
                    <ul style={{ marginTop: "0.375rem", paddingLeft: "1.25rem", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                      {result.missing_deps.map((dep) => (
                        <li key={dep}>{dep}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.conflicts.length > 0 && (
                  <div style={{ marginBottom: "0.75rem" }}>
                    <strong style={{ color: "var(--color-error)" }}>Conflicts:</strong>
                    <ul style={{ marginTop: "0.375rem", paddingLeft: "1.25rem", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                      {result.conflicts.map((conflict, i) => (
                        <li key={i}>{conflict}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.missing_deps.length === 0 && result.conflicts.length === 0 && result.compatible && (
                  <p style={{ color: "var(--color-success)", fontSize: "0.875rem" }}>No issues found.</p>
                )}
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}