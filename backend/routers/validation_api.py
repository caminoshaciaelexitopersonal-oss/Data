from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict, Any

from backend.services.validation_rules import ValidationService, get_validation_service

router = APIRouter(prefix="/validation", tags=["Validation"])

class ValidationRequest(BaseModel):
    data: List[Dict[str, Any]]
    rules: List[Dict[str, Any]]

@router.post("/run")
async def run_validation(
    request: ValidationRequest
):
    """
    Runs a set of validation rules against a given dataset.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided.")

    df = pd.DataFrame(request.data)

    # The rules are passed in the request, making it dynamic
    validator = get_validation_service(request.rules)

    if validator.validate(df):
        return {"status": "success", "message": "Validation passed."}
    else:
        return {"status": "failure", "errors": validator.get_errors()}
