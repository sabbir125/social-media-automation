import logging
import time
from src.config import SCHEDULE_INTERVAL_SEC
from src.orchestrator import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Instagram scraper starting. Interval: %ds", SCHEDULE_INTERVAL_SEC)
    while True:
        success = run()
        if not success:
            logger.error("Scrape cycle failed. Shutting down.")
            break
        logger.info("Cycle done. Next run in %ds.", SCHEDULE_INTERVAL_SEC)
        time.sleep(SCHEDULE_INTERVAL_SEC)
