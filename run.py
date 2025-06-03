import subprocess
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def run_backend():
    logger.info("🚀 Запускаю Backend...")
    return subprocess.Popen(["uvicorn", "main:app", "--reload"], cwd="backend")


def run_bot():
    logger.info("🚀 Запускаю Телеграм-бот...")
    return subprocess.Popen(["python", "main.py"], cwd="bot")


def main():
    backend_process = run_backend()
    bot_process = run_bot()

    try:
        while True:
            if backend_process.poll() is not None or bot_process.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Остановка процессов по KeyboardInterrupt.")
        backend_process.terminate()
        bot_process.terminate()
        backend_process.wait()
        bot_process.wait()
        sys.exit(0)

    logger.info(f"Backend завершился с кодом: {backend_process.returncode}")
    logger.info(f"Бот завершился с кодом: {bot_process.returncode}")


if __name__ == "__main__":
    main()
