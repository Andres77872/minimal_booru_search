from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from src.routes.nn import PicSearch, Pic2Encoder_picsearch

import time



app = FastAPI()


app.include_router(Pic2Encoder_picsearch.router,
                   prefix='/pic2encoder',
                   tags=['encoders'])
app.include_router(PicSearch.router,
                   prefix='/picsearch',
                   tags=['pic search'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/", include_in_schema=False)
async def root():
    response = RedirectResponse(url='/docs')
    return response


app.add_middleware(SessionMiddleware, secret_key="RULE_THE_WORLD")
