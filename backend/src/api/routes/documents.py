from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from src.services.document_service import DocumentService

router = APIRouter()

class DocumentRequest(BaseModel):
    title: str
    content: str
    source_type: Optional[str] = "BOOK_FULL"  # 'BOOK_FULL' or 'BOOK_SELECTION'

class DocumentResponse(BaseModel):
    document_id: str
    status: str  # 'PROCESSING', 'INDEXED', 'ERROR'
    message: str

class GetDocumentResponse(BaseModel):
    document_id: str
    title: str
    source_type: str
    metadata: dict
    status: str  # 'PROCESSING', 'INDEXED', 'ARCHIVED'
    created_at: str

@router.post("/documents", response_model=DocumentResponse)
async def create_document(document_request: DocumentRequest):
    try:
        service = DocumentService()
        doc_id = str(uuid.uuid4())
        
        status, message = service.create_document(
            doc_id=doc_id,
            title=document_request.title,
            content=document_request.content,
            source_type=document_request.source_type
        )
        
        return DocumentResponse(
            document_id=doc_id,
            status=status,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}", response_model=GetDocumentResponse)
async def get_document(document_id: str):
    try:
        service = DocumentService()
        doc = service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return GetDocumentResponse(
            document_id=doc['id'],
            title=doc['title'],
            source_type=doc['source_type'],
            metadata=doc['metadata'],
            status=doc['status'],
            created_at=doc['created_at']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))