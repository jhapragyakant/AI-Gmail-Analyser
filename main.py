import multiprocessing.process

# Monkey-patch multiprocessing to silently swallow KeyboardInterrupt in child processes.
# This prevents the ugly tracebacks Uvicorn produces on Windows when using reload=True.
_original_run = multiprocessing.process.BaseProcess.run

def _patched_run(self, *args, **kwargs):
    try:
        return _original_run(self, *args, **kwargs)
    except KeyboardInterrupt:
        pass

multiprocessing.process.BaseProcess.run = _patched_run

import uvicorn
import sys
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting AI Gmail Analyser server...")
        uvicorn.run(
            "backend.main:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n")
        logger.info("Shutdown requested by user (Ctrl+C).")
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
