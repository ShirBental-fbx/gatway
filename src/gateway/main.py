from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from gateway.errors.exceptions import FundboxAPIException
from gateway.errors.handlers import (
    fundbox_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="API Gateway (FastAPI)")

app.add_exception_handler(FundboxAPIException, fundbox_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/health")
def health():
    return {"status": "ok"}
