from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from collector.pipeline import run_collection
from storage import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def scheduled_collection() -> None:
    result = run_collection()
    logger.info("Collection finished: %s", result)


def main() -> None:
    initialize_database()
    scheduled_collection()

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(scheduled_collection, "interval", hours=24, id="world-bank-collection")
    logger.info("Scheduler started. Collection runs every 24 hours.")
    scheduler.start()


if __name__ == "__main__":
    main()
