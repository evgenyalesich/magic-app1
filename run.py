from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Final

# ──────────  stdout → UTF-8 (Windows)  ──────────
if hasattr(sys.stdout, "reconfigure"):  # Py 3.7+
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # на всякий случай
        pass

# ──────────  базовый логгер  ──────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%H:%M:%S",
    )
)
logging.basicConfig(level=LOG_LEVEL, handlers=[_handler])

log = logging.getLogger("runner")

ROOT: Final = Path(__file__).resolve().parent  # = project root


def _stream(proc: subprocess.Popen, prefix: str) -> None:
    """Проксируем выходной поток подпроцесса в общий лог."""
    with proc.stdout:  # type: ignore[attr-defined]
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode(errors="replace").rstrip()
            if line:  # пустые не печатаем
                log.debug("[%s] %s", prefix, line)
    proc.stdout.close()  # type: ignore[attr-defined]


def _spawn(cmd: list[str], cwd: Path, prefix: str) -> subprocess.Popen:
    log.info("▶️  %s (cwd=%s)", " ".join(cmd), cwd)

    # наследуем текущие переменные + добавляем/переопределяем нужные
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,  # ← вот эта строка
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,  # line-buffered
    )
    log.info("[%s] pid=%s", prefix, proc.pid)

    # отдельный поток, чтобы не блокировать основной цикл
    threading.Thread(
        target=_stream,
        args=(proc, prefix),
        daemon=True,
    ).start()
    return proc


def start_backend() -> subprocess.Popen:
    """
    Стартуем Uvicorn из корня проекта, чтобы import backend.*
    работал как пакет.  PYTHONPATH не трогаем – достаточно
    корректного cwd и backend.main:app.
    """
    return _spawn(
        ["uvicorn", "backend.main:app", "--reload", "--log-level", LOG_LEVEL.lower()],
        ROOT,  # <─ cwd = корень!
        "backend",
    )


def start_bot() -> subprocess.Popen:
    return _spawn(
        ["python", "main.py"],
        ROOT / "bot",
        "bot",
    )


def wait(proc: subprocess.Popen, name: str) -> None:
    """Блокируемся, дожидаясь завершения процесса и логируем код возврата."""
    rc = proc.wait()
    if rc == 0:
        log.info("✅ %s завершился (exit-code 0)", name)
    else:
        log.warning("💥 %s ушёл с кодом %s", name, rc)


def graceful_kill(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    """SIGTERM → ждём → SIGKILL."""
    if proc.poll() is not None:
        return
    log.info("⏹  Завершаю %s …", name)
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        log.warning("⛔ %s не завершился за %ss → kill", name, timeout)
        proc.kill()
        proc.wait()


def main() -> None:
    backend = start_backend()
    bot = start_bot()

    try:
        while True:
            if backend.poll() is not None or bot.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info("👋 Ctrl-C – останавливаем всё")

    graceful_kill(backend, "backend")
    graceful_kill(bot, "bot")

    # дожидаемся потоков-читалок; иначе в IDE последняя строка может «съесться»
    time.sleep(0.2)
    log.info("🏁 runner завершён")


if __name__ == "__main__":
    main()
