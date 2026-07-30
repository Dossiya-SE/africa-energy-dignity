import { describe, expect, it } from "vitest";

import {
  evidenceTone,
  formatTemporalCoverage,
  humanize,
  verificationTone,
} from "@/lib/presentation";

describe("evidence presentation", () => {
  it("humanizes canonical identifiers", () => {
    expect(humanize("source_verified")).toBe("Source Verified");
  });

  it("keeps unverified evidence visibly cautionary", () => {
    expect(evidenceTone("unverified")).toBe("warning");
  });

  it("treats validated states as positive", () => {
    expect(verificationTone("validated")).toBe("positive");
  });

  it("formats bounded temporal coverage", () => {
    expect(
      formatTemporalCoverage({ valid_from: "2024-01-01", valid_to: "2025-01-01" }),
    ).toBe("2024-01-01 to 2025-01-01");
  });

  it("does not invent missing temporal coverage", () => {
    expect(formatTemporalCoverage({})).toBe("Unknown");
  });
});
