import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { api, HealthResponse, SkillsResponse, CategoriesResponse } from "../src/api/client";

const mockSkillsResponse: SkillsResponse = {
  items: [
    {
      id: "test-skill-1",
      name: "Test Skill 1",
      description: "A test skill",
      category: "test",
      tags: ["test", "example"],
      repo_url: "https://github.com/test/skill1",
      install_command: "pip install test-skill-1",
      version: "1.0.0",
      dependencies: [],
    },
  ],
  total: 1,
  page: 1,
  page_size: 12,
};

const mockCategoriesResponse: CategoriesResponse = {
  categories: ["test", "orchestration", "rag"],
};

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(api, "listSkills").mockResolvedValue(mockSkillsResponse);
    vi.spyOn(api, "getCategories").mockResolvedValue(mockCategoriesResponse);
  });

  it("renders loading state initially", () => {
    // Don't resolve the promise to test loading state
    const { promise, resolve } = Promise.withResolvers<HealthResponse>();
    vi.spyOn(api, "health").mockReturnValue(promise);

    render(<App />);

    expect(screen.getByText("Checking backend connection…")).toBeInTheDocument();
    resolve({ status: "ok", service: "sentinel-station" });
  });

  it("renders health data on successful response", async () => {
    vi.spyOn(api, "health").mockResolvedValue({
      status: "ok",
      service: "sentinel-station",
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("ok")).toBeInTheDocument();
      expect(screen.getByText("sentinel-station")).toBeInTheDocument();
    });
  });

  it("renders error state on failed response", async () => {
    vi.spyOn(api, "health").mockRejectedValue(new Error("Connection refused"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Connection refused")).toBeInTheDocument();
    });
  });

  it("displays available endpoints list", async () => {
    vi.spyOn(api, "health").mockResolvedValue({
      status: "ok",
      service: "sentinel-station",
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Available Endpoints")).toBeInTheDocument();
      expect(screen.getByText("GET /api/v1/health")).toBeInTheDocument();
      expect(screen.getByText("GET /api/v1/skills")).toBeInTheDocument();
    });
  });
});
