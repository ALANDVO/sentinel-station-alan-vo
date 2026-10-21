import { Skill } from "../api/client";

interface SkillCardProps {
  skill: Skill;
  onSelect?: (skill: Skill) => void;
  selected?: boolean;
}

export function SkillCard({ skill, onSelect, selected }: SkillCardProps) {
  const handleClick = () => {
    if (onSelect) onSelect(skill);
  };

  return (
    <article
      className="card"
      style={{
        cursor: onSelect ? "pointer" : "default",
        transition: "border-color 0.15s, box-shadow 0.15s",
        borderLeft: selected ? "4px solid var(--color-primary)" : "none",
        background: selected ? "rgba(88, 166, 255, 0.05)" : "var(--color-surface)",
      }}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleClick();
        }
      }}
      tabIndex={onSelect ? 0 : undefined}
    >
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
        <div>
          <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "0.25rem" }}>
            {skill.name}
          </h3>
          <span className="badge">{skill.category}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span className="badge" style={{ fontSize: "0.7rem" }}>{skill.version}</span>
          {selected && (
            <span className="badge badge-success" style={{ fontSize: "0.7rem" }}>
              Selected
            </span>
          )}
        </div>
      </header>

      <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem", marginBottom: "1rem", lineHeight: 1.5 }}>
        {skill.description}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem", marginBottom: "1rem" }}>
        {skill.tags.slice(0, 5).map((tag) => (
          <span key={tag} className="badge" style={{ background: "var(--color-border)", color: "var(--color-text-muted)" }}>
            {tag}
          </span>
        ))}
        {skill.tags.length > 5 && (
          <span className="badge" style={{ background: "var(--color-border)", color: "var(--color-text-muted)" }}>
            +{skill.tags.length - 5} more
          </span>
        )}
      </div>

      <footer style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "0.75rem", borderTop: "1px solid var(--color-border)", fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
        <code style={{ fontFamily: "var(--font-mono)", background: "var(--color-bg)", padding: "0.125rem 0.375rem", borderRadius: "4px" }}>
          {skill.install_command}
        </code>
        <a href={skill.repo_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
          View Repo →
        </a>
      </footer>
    </article>
  );
}