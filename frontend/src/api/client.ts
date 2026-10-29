/** Typed API client for Sentinel Station backend. */

const API_BASE = "/api/v1";

export interface HealthResponse {
  status: string;
  service: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  repo_url: string;
  install_command: string;
  version: string;
  dependencies: string[];
}

export interface SkillsResponse {
  items: Skill[];
  total: number;
  page: number;
  page_size: number;
}

export interface CategoriesResponse {
  categories: string[];
}

export interface TagsResponse {
  tags: string[];
}

export interface ValidateRequest {
  skill_ids: string[];
}

export interface ValidationResult {
  skill_id: string;
  compatible: boolean;
  conflicts: string[];
  missing_deps: string[];
}

export interface ValidateResponse {
  results: ValidationResult[];
  overall_compatible: boolean;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  listSkills: (params: {
    page?: number;
    page_size?: number;
    category?: string;
    tag?: string;
    q?: string;
  } = {}) => {
    const search = new URLSearchParams();
    if (params.page) search.set("page", String(params.page));
    if (params.page_size) search.set("page_size", String(params.page_size));
    if (params.category) search.set("category", params.category);
    if (params.tag) search.set("tag", params.tag);
    if (params.q) search.set("q", params.q);
    return request<SkillsResponse>(`/skills?${search.toString()}`);
  },

  getSkill: (id: string) => request<Skill>(`/skills/${id}`),

  getCategories: () => request<CategoriesResponse>("/skills/categories"),

  getTags: () => request<TagsResponse>("/skills/tags"),

  validateStack: (skillIds: string[]) =>
    request<ValidateResponse>("/validate", {
      method: "POST",
      body: JSON.stringify({ skill_ids: skillIds }),
    }),
};
