"""Pulse — a tiny piece of app middleware (streaming-safe).

Declared in ``pyxle.config.json`` (``"middleware": ["middleware:ServerTimingMiddleware"]``),
this stamps a ``Server-Timing`` header with the handling time — visible in
DevTools → Network → Timing. It exists to show the custom-middleware system end
to end; the framework's own request-id and timing come from the ``observability``
block in the same config.

It is written as a **pure ASGI** middleware on purpose. A ``BaseHTTPMiddleware``
buffers the whole response, which is incompatible with Pyxle's streaming SSR: a
genuinely-deferred ``<Suspense>`` boundary turns the page into a chunked
``StreamingResponse``, and ``BaseHTTPMiddleware`` then raises
``RuntimeError: No response returned.``. A pure-ASGI middleware only rewrites the
``http.response.start`` headers and passes every body chunk straight through, so
it works on streamed and buffered responses alike. (See pyxle CORE_FINDINGS F28.)
"""

from __future__ import annotations

import time

from starlette.datastructures import MutableHeaders


class ServerTimingMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                headers = MutableHeaders(scope=message)
                headers["Server-Timing"] = f'app;desc="Pulse handler";dur={elapsed_ms:.1f}'
            await send(message)

        await self.app(scope, receive, send_wrapper)
