from __future__ import annotations

import argparse
import multiprocessing

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Exodia local backend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        access_log=False,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

