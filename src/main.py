"""Scheduler entrypoint. Runs blocking loop of 4 report crons + daily backup +
a lightweight Telegram polling loop for /stats.

Run as: python -m src.main
"""
from __future__ import annotations

import asyncio
import logging
import signal
import threading
from datetime import datetime

from src import config, db, scheduler, slash_commands, telegram_send

log = logging.getLogger(__name__)


async def _poll_telegram_updates() -> None:
    """Long-poll Telegram getUpdates for /stats. Runs in async task alongside APScheduler."""
    import aiohttp  # lazy — only needed for polling

    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        log.warning("TELEGRAM_BOT_TOKEN missing — /stats polling disabled")
        return
    offset: int | None = None
    async with aiohttp.ClientSession() as sess:
        while True:
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {"timeout": 30}
                if offset is not None:
                    params["offset"] = offset
                async with sess.get(url, params=params, timeout=40) as r:
                    data = await r.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message") or update.get("channel_post")
                    if not msg:
                        continue
                    text = (msg.get("text") or "").strip()
                    chat_id = str(msg["chat"]["id"])
                    if text.split()[0].lower() in {"/stats", "/stats@"}:
                        now_ist = datetime.now(config.TZ_IST).strftime("%Y-%m-%d %H:%M")
                        reply = slash_commands.handle_stats(chat_id, now_ist)
                        if reply is None:
                            log.info("stats rate-limited for chat %s", chat_id)
                            continue
                        telegram_send.send(reply, chat_id=chat_id)
            except Exception as e:
                log.warning("telegram poll error: %s", e)
                await asyncio.sleep(5)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    db.init_db()

    sched = scheduler.build_scheduler()

    # /stats polling in background thread so APScheduler's blocking loop can own main.
    def _poll_thread() -> None:
        try:
            asyncio.run(_poll_telegram_updates())
        except Exception as e:
            log.exception("poll thread died: %s", e)

    threading.Thread(target=_poll_thread, daemon=True, name="telegram-poll").start()

    log.info(
        "starting scheduler (DRY_RUN=%s, provider=%s)",
        config.DRY_RUN, config.LLM_PROVIDER,
    )
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("shutting down")


if __name__ == "__main__":
    main()
