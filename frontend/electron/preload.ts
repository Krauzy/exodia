import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("exodia", {
  apiBaseUrl: process.env.EXODIA_BACKEND_URL || "http://127.0.0.1:8765",
  platform: process.platform,
});

