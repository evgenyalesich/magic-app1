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
    except Exception:  # pragma: no cover
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
ROOT: Final = Path(__file__).resolve().parent  # корень проекта
BACKEND_DIR: Final = ROOT / "backend"
BOT_DIR: Final = ROOT / "bot"


# ─────────────────────────── вспомогательные ────────────────────────────
def _stream(proc: subprocess.Popen, prefix: str) -> None:
    """Проксируем stdout подпроцесса в общий лог."""
    with proc.stdout:  # type: ignore[attr-defined]
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode(errors="replace").rstrip()
            if line:
                log.debug("[%s] %s", prefix, line)


def _spawn(cmd: list[str], cwd: Path, prefix: str) -> subprocess.Popen:
    """Запускает подпроцесс + отдельный поток-логгер."""
    log.info("▶️  %s (cwd=%s)", " ".join(cmd), cwd)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # добавляем корень проекта в PYTHONPATH, чтобы backend.* импортировался в reloader
    root_str = str(ROOT)
    env["PYTHONPATH"] = (
        root_str + os.pathsep + env.get("PYTHONPATH", "")
        if env.get("PYTHONPATH")
        else root_str
    )

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,  # line-buffered
    )
    log.info("[%s] pid=%s", prefix, proc.pid)

    threading.Thread(target=_stream, args=(proc, prefix), daemon=True).start()
    return proc


def start_backend() -> subprocess.Popen:
    return _spawn(
        ["uvicorn", "backend.main:app", "--reload", "--log-level", LOG_LEVEL.lower()],
        ROOT,  # cwd = корень, чтобы backend был пакетом
        "backend",
    )


def start_bot() -> subprocess.Popen:
    return _spawn(["python", "main.py"], BOT_DIR, "bot")


def graceful_kill(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    """SIGTERM → ждём → SIGKILL, если процесс «залип»."""
    if proc.poll() is not None:
        return
    log.info("⏹  Завершаю %s …", name)
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        log.warning("⛔ %s не вышел за %ss → kill", name, timeout)
        proc.kill()
        proc.wait()


def wait_keyboard_interrupt(backend: subprocess.Popen, bot: subprocess.Popen) -> None:
    """Главный цикл – ждём завершения дочерних процессов или Ctrl-C."""
    try:
        while True:
            if backend.poll() is not None or bot.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info("👋 Ctrl-C – останавливаем всё")


# ─────────────────────────────── main ────────────────────────────────────
def main() -> None:
    backend = start_backend()
    bot = start_bot()

    wait_keyboard_interrupt(backend, bot)

    graceful_kill(backend, "backend")
    graceful_kill(bot, "bot")

    # небольшая пауза, чтобы потоки-логгеры успели дописать строки
    time.sleep(0.3)
    log.info("🏁 runner завершён")


if __name__ == "__main__":
    main()
