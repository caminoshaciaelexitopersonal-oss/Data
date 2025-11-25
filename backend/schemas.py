from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    llm_preference: Optional[str] = None

class PredictionRequest(BaseModel):
    run_id: str
    data: List[Dict[str, Any]]

class PipelineRequest(BaseModel):
    data: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]

class DataHealthRequest(BaseModel):
    data: List[Dict[str, Any]]

class MongoConnectionRequest(BaseModel):
    mongo_uri: str
    db_name: str
    collection_name: str

class DbConnectionRequest(BaseModel):
    db_uri: str
    query: str

class S3ConnectionRequest(BaseModel):
    bucket_name: str
    object_key: str

class SessionRequest(BaseModel):
    session_id: str
