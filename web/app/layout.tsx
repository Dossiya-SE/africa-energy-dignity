import type { Metadata } from "next";
import type { ReactNode } from "react";

import "maplibre-gl/dist/maplibre-gl.css";
import "@/app/globals.css";

import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: {
    default: "AED Studio",
    template: "%s | AED Studio",
  },
  description:
    "Africa Energy Dignity evidence, geography and decision-support workspace.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteHeader />
        <main className="page-shell">{children}</main>
        <footer className="site-footer">
          <p>
            Africa Energy Dignity — evidence must remain traceable, uncertainty visible and
            decisions accountable.
          </p>
        </footer>
      </body>
    </html>
  );
}
