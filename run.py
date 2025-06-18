from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Final

# ─────────────────────── stdout → UTF-8 (Windows) ───────────────────────
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ───────────────────────────── базовый логгер ───────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", "%H:%M:%S")
)
logging.basicConfig(level=LOG_LEVEL, handlers=[_handler])
log = logging.getLogger("runner")

# ────────────────────────────── константы ───────────────────────────────
ROOT: Final = Path(__file__).resolve().parent
BACKEND_DIR: Final = ROOT / "backend"
BOT_DIR: Final = ROOT / "bot"

log.debug("Runner root directory: %s", ROOT)
log.debug("Backend directory: %s", BACKEND_DIR)
log.debug("Bot directory: %s", BOT_DIR)
log.debug("Effective LOG_LEVEL: %s", LOG_LEVEL)

# ─────────────────────────── вспомогательные ────────────────────────────
def _stream(proc: subprocess.Popen, prefix: str) -> None:
    log.debug("[%s] stream thread started", prefix)
    with proc.stdout:
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode(errors="replace").rstrip()
            if line:
                log.debug("[%s] %s", prefix, line)
    log.debug("[%s] stream thread ended", prefix)

def _spawn(cmd: list[str], cwd: Path, prefix: str) -> subprocess.Popen:
    log.info("▶️  Spawning %s in %s", " ".join(cmd), cwd)
    # Собираем env и логируем ключевые переменные
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    root_str = str(ROOT)
    env["PYTHONPATH"] = root_str + os.pathsep + env.get("PYTHONPATH", "")
    debug_env = {
        "LOG_LEVEL": env.get("LOG_LEVEL"),
        "VITE_API_BASE": env.get("VITE_API_BASE"),
        "VITE_API_BASE_URL": env.get("VITE_API_BASE_URL"),
        "TELEGRAM_BOT_TOKEN": bool(env.get("TELEGRAM_BOT_TOKEN")),  # только факт наличия
    }
    log.debug("[%s] Environment variables: %s", prefix, debug_env)

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    log.info("[%s] Started process, pid=%s", prefix, proc.pid)

    thread = threading.Thread(target=_stream, args=(proc, prefix), daemon=True)
    thread.start()
    log.debug("[%s] Stream thread %s launched", prefix, thread.name)
    return proc

def start_backend() -> subprocess.Popen:
    log.debug(">> start_backend()")
    return _spawn(
        ["uvicorn", "backend.main:app", "--reload", "--log-level", LOG_LEVEL.lower()],
        ROOT,
        "backend",
    )

def start_bot() -> subprocess.Popen:
    log.debug(">> start_bot()")
    return _spawn(["python", "main.py"], BOT_DIR, "bot")

def graceful_kill(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    log.debug(">> graceful_kill(%s)", name)
    if proc.poll() is not None:
        log.debug("%s already terminated", name)
        return
    log.info("⏹  Terminating %s (pid=%s)…", name, proc.pid)
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
        log.info("%s exited cleanly", name)
    except subprocess.TimeoutExpired:
        log.warning("⛔ %s did not exit in %ss, killing", name, timeout)
        proc.kill()
        proc.wait()
        log.info("%s force-killed", name)

def wait_keyboard_interrupt(backend: subprocess.Popen, bot: subprocess.Popen) -> None:
    log.debug(">> wait_keyboard_interrupt() loop start")
    try:
        while True:
            if backend.poll() is not None:
                log.warning("Backend process ended with code %s", backend.returncode)
                break
            if bot.poll() is not None:
                log.warning("Bot process ended with code %s", bot.returncode)
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info("👋 Ctrl-C received, stopping processes")

# ─────────────────────────────── main ────────────────────────────────────
def main() -> None:
    log.info("🏁 Runner starting services")
    backend = start_backend()
    bot = start_bot()
    log.info("Runner launched backend (pid=%s) and bot (pid=%s)", backend.pid, bot.pid)

    wait_keyboard_interrupt(backend, bot)

    log.info("Runner shutting down services")
    graceful_kill(backend, "backend")
    graceful_kill(bot, "bot")

    time.sleep(0.3)
    log.info("🏁 Runner finished")

if __name__ == "__main__":
    log.debug("Entry point __main__ reached")
    main()
