from starlette.responses import JSONResponse


async def endpoint(request):
    return JSONResponse({"status": "ok", "app": "glyph-demo"})
