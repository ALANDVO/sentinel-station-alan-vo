import { vi } from "vitest";
import "@testing-library/jest-dom";

// Mock fetch for tests
vi.stubGlobal("fetch", vi.fn());