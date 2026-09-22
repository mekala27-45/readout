import type { Metadata } from "next";
import { Shell } from "@/components/shell";
import "./globals.css";
export const metadata: Metadata = {
  title: {
    default: "readout | Decisions, with evidence",
    template: "%s | readout",
  },
  description:
    "An experimentation workbench. Check the assignment, measure the effect, make the decision. Every statistical claim is calibrated against known truth.",
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
