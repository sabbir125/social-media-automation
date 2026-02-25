import time
from src.config import SCHEDULE_INTERVAL_SEC
from src.orchestrator import run

if __name__ == "__main__":
    while True:
        result = run()
        if not result["success"] and result["error"] in ("listEmpty", "network"):
            print(f"Stopping: {result['error']}")
            break
        print(f"Sleeping for {SCHEDULE_INTERVAL_SEC}s...")
        time.sleep(SCHEDULE_INTERVAL_SEC)
