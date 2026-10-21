import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { api, HealthResponse } from "../src/api/client";

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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