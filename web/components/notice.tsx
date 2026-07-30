import type { ReactNode } from "react";

interface NoticeProps {
  title: string;
  children: ReactNode;
  tone?: "information" | "warning" | "error";
}

export function Notice({ title, children, tone = "information" }: NoticeProps) {
  return (
    <aside className={`notice notice-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <strong>{title}</strong>
      <div>{children}</div>
    </aside>
  );
}
