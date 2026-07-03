# Security Model

Exodia is a defensive local audit tool. The default posture is safe mode.

## Allowed Behavior

- Passive HTTP observation.
- TLS certificate and protocol inspection.
- Low-rate TCP connection checks against a small allowlisted port set.
- Local-only plugin loading from a configured directory.
- Technical reports focused on impact, evidence, and mitigation.

## Explicitly Excluded Behavior

- Credential theft.
- Phishing.
- Malware.
- Persistence.
- Evasion or stealth scanning.
- Firewall bypass.
- Brute force.
- Reverse shells.
- Exfiltration.
- Destructive payloads.
- Automated exploitation against unauthorized third parties.

## Controls

- Targets require validated URL, host, or IP input.
- Web/API targets only allow `http` and `https`.
- Scans require explicit authorization confirmation.
- User authentication is required for targets, scans, reports, settings, and active check endpoints.
- Targets, scan history, and reports are scoped to the authenticated user.
- Built-in modules avoid command execution.
- Safe Port Probe only checks a small default port list.
- HTTP requests use timeouts.
- Reports include an authorized-use disclaimer.
- Electron renderer runs with Node integration disabled and context isolation enabled.

## Plugin Boundary

Plugins are local Python modules loaded from a configured folder. Exodia does not download plugin code from the internet. Operators must review plugin code before enabling it.
