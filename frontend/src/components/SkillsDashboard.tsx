import { useState, useEffect, useCallback } from "react";
import { api, Skill } from "../api/client";
import { SkillCard } from "./SkillCard";

interface SkillsDashboardProps {
  initialCategory?: string;
}

export function SkillsDashboard({ initialCategory }: SkillsDashboardProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [category, setCategory] = useState(initialCategory || "");
  const [tag, setTag] = useState("");
  const [query, setQuery] = useState("");

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listSkills({ page, page_size: pageSize, category: category || undefined, tag: tag || undefined, q: query || undefined });
      setSkills(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load skills");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, category, tag, query]);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const totalPages = Math.ceil(total / pageSize) || 1;

  const handleCategoryChange = (cat: string) => {
    setCategory(cat);
    setPage(1);
  };

  const handleTagChange = (t: string) => {
    setTag(t);
    setPage(1);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  if (loading) {
    return <div className="loading">Loading skills catalog…</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      {/* Filters */}
      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "flex-end" }}>
          <div style={{ flex: 1, minWidth: "200px" }}>
            <label htmlFor="search" style={{ display: "block", marginBottom: "0.375rem", fontSize: "0.875rem", fontWeight: "500" }}>
              Search
            </label>
            <input
              id="search"
              type="search"
              className="input"
              placeholder="Search skills…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <div style={{ minWidth: "180px" }}>
            <label htmlFor="category" style={{ display: "block", marginBottom: "0.375rem", fontSize: "0.875rem", fontWeight: "500" }}>
              Category
            </label>
            <select id="category" className="input" value={category} onChange={(e) => handleCategoryChange(e.target.value)}>
              <option value="">All Categories</option>
              <option value="orchestration">Orchestration</option>
              <option value="rag">RAG</option>
              <option value="vector-db">Vector DB</option>
              <option value="optimization">Optimization</option>
              <option value="prompting">Prompting</option>
              <option value="llm-client">LLM Client</option>
              <option value="ml-framework">ML Framework</option>
              <option value="observability">Observability</option>
              <option value="mlops">MLOps</option>
            </select>
          </div>

          <div style={{ minWidth: "150px" }}>
            <label htmlFor="tag" style={{ display: "block", marginBottom: "0.375rem", fontSize: "0.875rem", fontWeight: "500" }}>
              Tag
            </label>
            <input
              id="tag"
              type="text"
              className="input"
              placeholder="Filter by tag"
              value={tag}
              onChange={(e) => handleTagChange(e.target.value)}
            />
          </div>
        </form>
      </section>

      {/* Results */}
      <section>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.25rem" }}>
            Skills Catalog
            {total > 0 && <span style={{ marginLeft: "0.75rem", color: "var(--color-text-muted)", fontWeight: "normal", fontSize: "1rem" }}>
              ({total} total)
            </span>}
          </h2>
        </header>

        {skills.length === 0 ? (
          <div className="empty">
            <p>No skills found matching your criteria.</p>
            <p style={{ marginTop: "0.5rem", fontSize: "0.875rem" }}>Try adjusting your filters or search query.</p>
          </div>
        ) : (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
              {skills.map((skill) => (
                <SkillCard key={skill.id} skill={skill} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <nav style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "0.5rem" }} aria-label="Pagination">
                <button
                  className="btn btn-secondary"
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  aria-label="Previous page"
                >
                  ← Prev
                </button>
                <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    let pageNum: number;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (page <= 3) {
                      pageNum = i + 1;
                    } else if (page >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }
                    return (
                      <button
                        key={pageNum}
                        className={`btn ${page === pageNum ? "btn-primary" : "btn-secondary"}`}
                        onClick={() => setPage(pageNum)}
                        aria-current={page === pageNum ? "page" : undefined}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </span>
                <button
                  className="btn btn-secondary"
                  disabled={page >= totalPages}
                  onClick={() => setPage(page + 1)}
                  aria-label="Next page"
                >
                  Next →
                </button>
              </nav>
            )}
          </>
        )}
      </section>
    </div>
  );
}