import { ShieldAlert } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { SectionHeader } from "../../components/ui/SectionHeader";

export function AboutPage() {
  return (
    <>
      <SectionHeader title="About" description="Exodia desktop defensive audit platform." />
      <Card>
        <div className="flex items-start gap-4">
          <div className="rounded-md border border-cyan-400/30 bg-cyan-400/10 p-3">
            <ShieldAlert className="h-6 w-6 text-cyan-200" />
          </div>
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold text-zinc-50">Exodia 0.1.0</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">
                A local desktop console for authorized security analysis, vulnerability review,
                audit automation, and technical reporting. The application intentionally excludes
                destructive, evasive, persistent, credential theft, phishing, malware, and
                unauthorized exploitation features.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge>FastAPI</Badge>
              <Badge>Electron</Badge>
              <Badge>React</Badge>
              <Badge>SQLite</Badge>
              <Badge>SSE logs</Badge>
              <Badge>Local plugins</Badge>
            </div>
          </div>
        </div>
      </Card>
    </>
  );
}

