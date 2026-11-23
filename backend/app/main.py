from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .auth import router as auth_router

from .core.parser import inspect_source
from .core.repair import UnsupportedRepair, preview_available_repairs, preview_repair
from .core.verification import RepairValidationError
from .core.rules import RULES
from .schemas import BatchRepairPreview, ParseResult, RepairPreview, RepairRequest, RuleInfo, SourceRequest

app = FastAPI(title="CRISPR-ASR", version="0.1.0")
app.include_router(auth_router)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, error: RequestValidationError):
    if request.url.path.startswith("/api/auth/"):
        return JSONResponse(status_code=422, content={"detail": "Invalid account request."})
    return await request_validation_exception_handler(request, error)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/rules", response_model=list[RuleInfo])
def list_rules() -> list:
    return list(RULES.values())


@app.post("/api/parse", response_model=ParseResult)
def parse_source(request: SourceRequest) -> dict:
    try:
        return inspect_source(request.source)
    except SyntaxError as error:
        raise HTTPException(
            status_code=422,
            detail={"message": error.msg, "line": error.lineno, "column": error.offset},
        ) from error
    except (RecursionError, ValueError) as error:
        raise HTTPException(
            status_code=422, detail="Source could not be parsed."
        ) from error


@app.post("/api/repair-preview", response_model=RepairPreview)
def repair_preview(request: RepairRequest) -> dict:
    try:
        return preview_repair(request.source, request.rule_id, request.line, request.column)
    except UnsupportedRepair as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except RepairValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (SyntaxError, RecursionError, ValueError) as error:
        raise HTTPException(status_code=422, detail="Source could not be parsed for repair.") from error


@app.post("/api/repair-preview/all", response_model=BatchRepairPreview)
def batch_repair_preview(request: SourceRequest) -> dict:
    try:
        return preview_available_repairs(request.source)
    except UnsupportedRepair as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except RepairValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (SyntaxError, RecursionError, ValueError) as error:
        raise HTTPException(status_code=422, detail="Source could not be parsed for repair.") from error
