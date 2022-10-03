import secure

from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi_pagination import Page, add_pagination, paginate
from app.core import config
from app.api.v1 import routers
from fastapi.middleware.cors import CORSMiddleware

# server = secure.Server().set("Secure")

# csp = (
#     secure.ContentSecurityPolicy()
#         .default_src("'none'")
#         .base_uri("'self'")
#         # .connect_src("'self'" "api.spam.com")
#         .frame_src("'none'")
#     # .img_src("'self' ", "static.spam.com")
# )

# hsts = secure.StrictTransportSecurity().include_subdomains().preload().max_age(2592000)

# referrer = secure.ReferrerPolicy().no_referrer()

# permissions_value = (
#     secure.PermissionsPolicy().geolocation("self", "'spam.com'").vibrate()
# )

# cache_value = secure.CacheControl().must_revalidate()

# secure_headers = secure.Secure(
#     server=server,
#     # csp=csp,
#     hsts=hsts,
#     referrer=referrer,
#     # permissions=permissions_value,
#     cache=cache_value,
# )


app = FastAPI(
    title=str(config.PROJECT_NAME), docs_url="/api/docs", openapi_url="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     request.state.db = SessionLocal()
#     response = await call_next(request)
#     request.state.db.close()
#     secure_headers.framework.fastapi(response)
#     return response


# public routers

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


app.include_router(routers.auth_router, prefix=config.API_STR, tags=["auth"])

app.include_router(
    routers.public_router,
    prefix=config.MAP_URL('public'),
    tags=['public'],
)

# private routes
app.include_router(
    routers.user_router,
    prefix=config.MAP_URL('users'),
    tags=["users"]
)

app.include_router(
    routers.country_router,
    prefix=config.MAP_URL('countries'),
    tags=["countries"]
)

app.include_router(
    routers.module_router,
    prefix=config.MAP_URL('modules'),
    tags=["modules"]
)
app.include_router(
    routers.group_router,
    prefix=config.MAP_URL('groups'),
    tags=["groups"]
)
app.include_router(
    routers.menu_router,
    prefix=config.MAP_URL('menu'),
    tags=["menu"]
)
app.include_router(
    routers.permission_router,
    prefix=config.MAP_URL('permission'),
    tags=["permission"]
)

app.include_router(
    routers.files_router,
    prefix=config.MAP_URL('files'),
    tags=['File Upload'],
)

app.include_router(
    routers.city_router,
    prefix=config.MAP_URL('city'),
    tags=["city"]
)

#graphql
from app.gpql.controller import gpql_country
app.include_router(gpql_country)


add_pagination(app)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8802)
