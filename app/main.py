# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import time
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from app import config as cfg
from app.api.routes import risk


app = FastAPI(
    title=cfg.PROJECT_NAME,
    description=cfg.PROJECT_DESCRIPTION,
    debug=cfg.DEBUG,
    version=cfg.VERSION,
)

# Routing
app.include_router(risk.router, prefix="/risk", tags=["risk"])


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=cfg.PROJECT_NAME,
        version=cfg.VERSION,
        description=cfg.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": cfg.LOGO_URL}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
