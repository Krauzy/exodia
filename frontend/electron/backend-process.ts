import { ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

import { app } from "electron";

const BACKEND_PORT = Number(process.env.EXODIA_BACKEND_PORT ?? "8765");
const BACKEND_HOST = "127.0.0.1";
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

let backendProcess: ChildProcessWithoutNullStreams | undefined;

export function getBackendUrl() {
  return BACKEND_URL;
}

function sqliteUrl(filePath: string) {
  return `sqlite:///${filePath.replace(/\\/g, "/")}`;
}

export function startBackend() {
  if (backendProcess && !backendProcess.killed) {
    return backendProcess;
  }

  const packagedBackendDir = path.join(process.resourcesPath, "backend");
  const packagedBackendExecutable = path.join(
    packagedBackendDir,
    process.platform === "win32" ? "exodia-backend.exe" : "exodia-backend",
  );
  const backendCwd =
    app.isPackaged && existsSync(packagedBackendExecutable)
      ? packagedBackendDir
      : app.isPackaged
        ? path.join(process.resourcesPath, "backend-source")
        : path.resolve(process.cwd(), "..", "backend");
  const localPython = path.join(
    backendCwd,
    ".venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );
  const usePackagedBackend = app.isPackaged && existsSync(packagedBackendExecutable);
  const backendCommand = usePackagedBackend
    ? packagedBackendExecutable
    : process.env.EXODIA_PYTHON || (existsSync(localPython) ? localPython : "python");
  const backendArgs = usePackagedBackend
    ? ["--host", BACKEND_HOST, "--port", String(BACKEND_PORT)]
    : ["-m", "uvicorn", "app.main:app", "--host", BACKEND_HOST, "--port", String(BACKEND_PORT)];
  const backendDataDir = path.join(app.getPath("userData"), "backend");
  const pluginsDir = path.join(backendDataDir, "plugins");
  mkdirSync(pluginsDir, { recursive: true });

  backendProcess = spawn(
    backendCommand,
    backendArgs,
    {
      cwd: backendCwd,
      env: {
        ...process.env,
        EXODIA_ALLOWED_ORIGINS: '["http://localhost:5173","http://127.0.0.1:5173","null"]',
        ...(app.isPackaged
          ? {
              EXODIA_DATABASE_URL: sqliteUrl(path.join(backendDataDir, "exodia.db")),
              EXODIA_PLUGINS_DIR: pluginsDir,
            }
          : {}),
      },
      stdio: "pipe",
      windowsHide: true,
    },
  );

  backendProcess.stdout.on("data", (data) => {
    console.log(`[backend] ${String(data).trim()}`);
  });
  backendProcess.stderr.on("data", (data) => {
    console.error(`[backend] ${String(data).trim()}`);
  });
  backendProcess.on("exit", (code) => {
    console.log(`[backend] exited with code ${code}`);
    backendProcess = undefined;
  });
  return backendProcess;
}

export async function waitForBackend(timeoutMs = 15_000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(`${BACKEND_URL}/health`);
      if (response.ok) return true;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 400));
    }
  }
  return false;
}

export function stopBackend() {
  if (!backendProcess || backendProcess.killed) return;
  backendProcess.kill("SIGTERM");
  backendProcess = undefined;
}
