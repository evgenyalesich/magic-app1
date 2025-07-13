from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import weakref
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

# It's good practice to handle potential import errors for optional dependencies.
try:
    import uvicorn
except ImportError:
    uvicorn = None

# --- Basic Logging Setup ---
# Suppress noisy exceptions on stream reconfiguration if it's not supported.
with suppress(Exception):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_log_formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", "%H:%M:%S")
_log_handler = logging.StreamHandler(sys.stdout)
_log_handler.setFormatter(_log_formatter)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    handlers=[_log_handler],
    force=True
)

# --- Service Configuration ---
@dataclass(frozen=True, slots=True)
class ServiceConfig:
    """Immutable service configuration with optimal memory layout."""

    # Use __file__ to get the path of the current script.
    root_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    backend_host: str = "0.0.0.0"
    backend_port: int = 443  # Default port for HTTPS
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    shutdown_timeout: float = 10.0
    monitor_interval: float = 1.0
    startup_delay: float = 2.0

    # SSL configuration read from environment variables
    ssl_certfile: Optional[str] = field(default_factory=lambda: os.getenv("SSL_CERTFILE"))
    ssl_keyfile:  Optional[str] = field(default_factory=lambda: os.getenv("SSL_KEYFILE"))

    @property
    def backend_dir(self) -> Path:
        """Returns the path to the backend directory."""
        return self.root_dir / "backend"

    @property
    def bot_dir(self) -> Path:
        """Returns the path to the bot directory."""
        return self.root_dir / "bot"

    def validate_ssl_config(self) -> tuple[bool, str]:
        """Validate SSL configuration and return status with a descriptive message."""
        if not self.ssl_certfile and not self.ssl_keyfile:
            return False, "SSL disabled - no certificate or key files specified via environment variables"

        if not self.ssl_certfile:
            return False, "SSL configuration error - missing SSL_CERTFILE"

        if not self.ssl_keyfile:
            return False, "SSL configuration error - missing SSL_KEYFILE"

        cert_path = Path(self.ssl_certfile)
        key_path = Path(self.ssl_keyfile)

        if not cert_path.exists():
            return False, f"SSL certificate file not found: {self.ssl_certfile}"

        if not key_path.exists():
            return False, f"SSL key file not found: {self.ssl_keyfile}"

        if not cert_path.is_file():
            return False, f"SSL certificate path is not a regular file: {self.ssl_certfile}"

        if not key_path.is_file():
            return False, f"SSL key path is not a regular file: {self.ssl_keyfile}"

        # Check if files are readable
        try:
            cert_path.read_bytes()
        except Exception as e:
            return False, f"Cannot read SSL certificate file: {e}"

        try:
            key_path.read_bytes()
        except Exception as e:
            return False, f"Cannot read SSL key file: {e}"

        return True, f"SSL configured successfully - cert: {cert_path.name}, key: {key_path.name}"


# --- Main Service Runner Class ---
class ServiceRunner:
    """Orchestrates the startup, monitoring, and shutdown of multiple services."""

    # Added '__weakref__' to __slots__ to allow weak referencing of ServiceRunner instances.
    __slots__ = ('_config', '_log', '_shutdown_event', '_executor', '_uvicorn_server', '_signal_handlers', '__weakref__')

    def __init__(self, config: Optional[ServiceConfig] = None) -> None:
        """Initializes the ServiceRunner."""
        self._config = config or ServiceConfig()
        # Correctly get the logger name using __name__ and the class name.
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._shutdown_event = asyncio.Event()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="service_pool")
        self._uvicorn_server: Optional[uvicorn.Server] = None
        self._signal_handlers: dict[int, Callable] = {}

        self._setup_paths()
        self._register_signal_handlers()
        self._log_ssl_configuration()

    def _log_ssl_configuration(self) -> None:
        """Logs the detailed SSL configuration status on startup."""
        self._log.info("🔐 SSL Configuration Check:")
        cert_env = os.getenv("SSL_CERTFILE")
        key_env = os.getenv("SSL_KEYFILE")
        self._log.info("   SSL_CERTFILE env: %s", cert_env or "not set")
        self._log.info("   SSL_KEYFILE env: %s", key_env or "not set")

        is_valid, message = self._config.validate_ssl_config()
        if is_valid:
            self._log.info("✅ %s", message)
            self._log.info("   Certificate: %s", self._config.ssl_certfile)
            self._log.info("   Private key: %s", self._config.ssl_keyfile)
        else:
            self._log.warning("⚠️  %s", message)
            if self._config.backend_port == 443:
                self._log.warning("   Port 443 is configured, but SSL is not. Consider changing to port 80 or fixing the SSL config.")

    def _setup_paths(self) -> None:
        """Adds service-related directories to the Python path."""
        paths_to_add = [str(self._config.bot_dir), str(self._config.root_dir)]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
        self._log.debug("Updated sys.path: %s", sys.path)

    def _register_signal_handlers(self) -> None:
        """Registers handlers for SIGINT and SIGTERM to trigger a graceful shutdown."""
        weak_self = weakref.ref(self)

        def signal_handler(signum: int, frame: Any) -> None:
            instance = weak_self()
            if instance:
                # Use call_soon_threadsafe for thread safety from a signal handler
                asyncio.get_running_loop().call_soon_threadsafe(instance._shutdown_event.set)
                self._log.info("👋 Received signal %s, initiating shutdown...", signal.strsignal(signum))

        for sig in (signal.SIGINT, signal.SIGTERM):
            self._signal_handlers[sig] = signal.signal(sig, signal_handler)

    @asynccontextmanager
    async def _managed_uvicorn_server(self):
        """A context manager to handle the lifecycle of the Uvicorn server."""
        if uvicorn is None:
            self._log.error("Uvicorn is not installed. Cannot run backend service. Please run 'pip install uvicorn'.")
            yield
            return

        try:
            # Dynamically import the FastAPI app
            from backend.main import app

            is_ssl_valid, ssl_message = self._config.validate_ssl_config()
            protocol = "https" if is_ssl_valid else "http"
            ssl_status = "🔒 SSL enabled" if is_ssl_valid else "🔓 SSL disabled"

            config = uvicorn.Config(
                app=app,
                host=self._config.backend_host,
                port=self._config.backend_port,
                log_level=self._config.log_level.lower(),
                reload=False,
                access_log=True,
                loop="asyncio",
                ssl_keyfile=self._config.ssl_keyfile if is_ssl_valid else None,
                ssl_certfile=self._config.ssl_certfile if is_ssl_valid else None,
            )
            self._uvicorn_server = uvicorn.Server(config)

            self._log.info("▶️  Backend server starting:")
            self._log.info("   Protocol: %s", protocol.upper())
            self._log.info("   Address:  %s://%s:%d", protocol, self._config.backend_host, self._config.backend_port)
            self._log.info("   Status:   %s", ssl_status)
            if not is_ssl_valid:
                self._log.info("   Reason:   %s", ssl_message)

            yield self._uvicorn_server
        finally:
            if self._uvicorn_server:
                self._log.debug("Uvicorn server marked for exit.")
                self._uvicorn_server.should_exit = True
                self._uvicorn_server = None

    async def _run_backend_service(self) -> None:
        """Runs the Uvicorn server within the thread pool."""
        async with self._managed_uvicorn_server() as server:
            if server:
                await self._executor_submit(server.run)

    async def _run_bot_service(self) -> None:
        """Runs the Telegram bot service."""
        try:
            from bot.main import dp, bot
            self._log.info("▶️  Starting Telegram bot service")
            # handle_signals=False prevents aiogram from conflicting with our handlers
            await dp.start_polling(bot, handle_signals=False)
        except ImportError as e:
            self._log.error("Bot import failed: %s. Ensure 'bot/main.py' exists and is correct.", e)
            raise
        except Exception as e:
            self._log.error("An error occurred in the bot service: %s", e)
            raise

    async def _executor_submit(self, func: Callable, *args: Any) -> Any:
        """Submits a function to the thread pool executor and handles exceptions."""
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(self._executor, func, *args)
        except Exception as e:
            self._log.error("Executor task failed: %s", e)
            self._shutdown_event.set()
            raise

    async def _monitor_services(self, *tasks: asyncio.Task) -> None:
        """Monitors running service tasks and triggers shutdown if any of them fail."""
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task.done() and (exc := task.exception()):
                self._log.error("Service task '%s' failed with an exception: %s", task.get_name(), exc)
                self._shutdown_event.set()

    async def _graceful_service_shutdown(self, *tasks: asyncio.Task) -> None:
        """Cancels all running tasks and waits for them to finish."""
        self._log.info("⏹️  Initiating graceful shutdown...")
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to acknowledge cancellation
        await asyncio.gather(*tasks, return_exceptions=True)

        # Shut down the thread pool
        self._executor.shutdown(wait=True, cancel_futures=True)
        self._log.info("✅ All services have been shut down.")

    async def _startup_sequence(self) -> list[asyncio.Task]:
        """Starts all services in a defined sequence."""
        self._log.info("🚀 Starting services...")
        backend_task = asyncio.create_task(self._run_backend_service(), name="backend_service")

        # Wait a moment before starting the next service
        await asyncio.sleep(self._config.startup_delay)

        bot_task = asyncio.create_task(self._run_bot_service(), name="bot_service")

        self._log.info("✅ All services have been initiated.")
        return [backend_task, bot_task]

    async def run_async(self) -> None:
        """The main asynchronous entry point for running the services."""
        tasks = []
        try:
            tasks = await self._startup_sequence()
            while not self._shutdown_event.is_set():
                await self._monitor_services(*tasks)
                # Sleep to prevent a tight loop if a service fails immediately
                await asyncio.sleep(self._config.monitor_interval)
        except Exception as e:
            self._log.critical("A critical error occurred during service orchestration: %s", e, exc_info=True)
            self._shutdown_event.set()
        finally:
            await self._graceful_service_shutdown(*tasks)

    def run(self) -> None:
        """The main synchronous entry point that sets up and runs the asyncio loop."""
        self._log.info("🏁 ServiceRunner initializing...")
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            self._log.info("👋 Keyboard interrupt received. Shutting down.")
        except Exception as e:
            self._log.critical("An unhandled runtime error occurred: %s", e, exc_info=True)
        finally:
            self._cleanup_resources()
            self._log.info("🏁 ServiceRunner finished.")

    def _cleanup_resources(self) -> None:
        """Restores original signal handlers and cleans up resources."""
        self._log.debug("Cleaning up resources...")
        for sig, handler in self._signal_handlers.items():
            if callable(handler):
                signal.signal(sig, handler)
        # Ensure executor is shut down even if run_async didn't complete
        if not self._executor._shutdown:
            self._executor.shutdown(wait=False, cancel_futures=True)
        self._log.debug("Resource cleanup complete.")


def main() -> None:
    """Main function to configure and run the service runner."""
    # Create placeholder directories and files for demonstration purposes
    # In a real application, these would already exist.
    Path("backend").mkdir(exist_ok=True)
    Path("bot").mkdir(exist_ok=True)
    Path("backend/main.py").touch(exist_ok=True)
    Path("bot/main.py").touch(exist_ok=True)

    # Example placeholder content
    Path("backend/main.py").write_text('app = "This is a placeholder for a FastAPI app"')
    Path("bot/main.py").write_text('class Mock: pass\nbot=Mock()\ndp=Mock()')


    config = ServiceConfig()
    runner = ServiceRunner(config)
    runner.run()


if __name__ == "__main__":
    # This check ensures the code runs only when the script is executed directly.
    main()
