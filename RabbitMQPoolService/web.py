from receiver import WorkerPool
from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    setup_aiohttp_apispec,
)
from aiohttp import web
from request_schema import RequestSchema


@docs(
    tags=["start"],
    summary="Start new pool",
    description="Start new pool",
)
@request_schema(RequestSchema())
async def start_pool(request):
    event_id = request.match_info.get('event_id', None)
    if event_id:
        payload = await request.json()
        if payload:
            wp: WorkerPool = WorkerPool(event_id, token=payload['token'], connection_string=payload['connection_string'])
            wp.up_workers()
            return web.json_response({"event_id": event_id})
    return web.Response(status=401)

app = web.Application()
app.add_routes([web.post('/pool/{event_id}', start_pool)])

if __name__ == '__main__':
    setup_aiohttp_apispec(
        app=app, 
        title="My Documentation", 
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )

    web.run_app(app, port=9999)