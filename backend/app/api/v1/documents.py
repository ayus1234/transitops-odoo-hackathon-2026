"""
Document API endpoints.
"""
from typing import List, Optional
from uuid import UUID
import os
import uuid as uuid_lib
from fastapi import APIRouter, Depends, Query, File, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentVerifyRequest,
    DocumentResponse,
    DocumentListResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.document_service import DocumentService


router = APIRouter()

# Local upload directory setup
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=PaginatedResponse[DocumentListResponse])
def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    verification_state: Optional[str] = Query(None, description="Filter by verification state"),
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle"),
    driver_id: Optional[UUID] = Query(None, description="Filter by driver"),
    maintenance_id: Optional[UUID] = Query(None, description="Filter by maintenance record"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor"),
    search: Optional[str] = Query(None, description="Search title, number, issuer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "read"))
):
    """
    Get list of documents with pagination and filters.

    Permissions: documents:read
    """
    service = DocumentService(db)
    docs, total = service.get_documents(
        page=page,
        page_size=page_size,
        document_type=document_type,
        status=status,
        verification_state=verification_state,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        maintenance_id=maintenance_id,
        vendor_id=vendor_id,
        search=search
    )

    return PaginatedResponse(
        success=True,
        data=[DocumentListResponse.model_validate(d) for d in docs],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.get("/expiring", response_model=List[DocumentListResponse])
def get_expiring_documents(
    days: int = Query(30, ge=1, le=180, description="Expiry threshold in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "read"))
):
    """
    Get documents expiring within threshold days (dashboard alert feed).

    Permissions: documents:read
    """
    service = DocumentService(db)
    docs = service.get_expiring_documents(threshold_days=days)
    return [DocumentListResponse.model_validate(d) for d in docs]


@router.get("/expired", response_model=List[DocumentListResponse])
def get_expired_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "read"))
):
    """
    Get all expired documents.

    Permissions: documents:read
    """
    service = DocumentService(db)
    docs = service.get_expired_documents()
    return [DocumentListResponse.model_validate(d) for d in docs]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "create"))
):
    """
    Create a document record metadata.

    Permissions: documents:create
    """
    service = DocumentService(db)
    doc = service.create_document(data, current_user)
    return DocumentResponse.model_validate(doc)


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document_file(
    file: UploadFile = File(...),
    current_user: User = Depends(PermissionChecker("documents", "create"))
):
    """
    Upload a file binary for a document.

    Permissions: documents:create
    """
    # Simple extension and file size validation
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}"
        )

    file_id = str(uuid_lib.uuid4())
    saved_filename = f"{file_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    contents = await file.read()
    file_size = len(contents)

    with open(saved_path, "wb") as f:
        f.write(contents)

    return {
        "success": True,
        "file_name": file.filename,
        "file_path": saved_path,
        "file_size_bytes": file_size,
        "mime_type": file.content_type
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "read"))
):
    """
    Get document by ID.

    Permissions: documents:read
    """
    service = DocumentService(db)
    doc = service.get_document(document_id)
    return DocumentResponse.model_validate(doc)


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "update"))
):
    """
    Update document metadata.

    Permissions: documents:update
    """
    service = DocumentService(db)
    doc = service.update_document(document_id, data, current_user)
    return DocumentResponse.model_validate(doc)


@router.patch("/{document_id}/verify", response_model=DocumentResponse)
def verify_document(
    document_id: UUID,
    req: DocumentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "update"))
):
    """
    Verify or reject a document.

    Permissions: documents:update
    """
    service = DocumentService(db)
    doc = service.verify_document(document_id, req, current_user)
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", response_model=SuccessResponse)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("documents", "delete"))
):
    """
    Delete a document.

    Permissions: documents:delete
    """
    service = DocumentService(db)
    service.delete_document(document_id, current_user)
    return SuccessResponse(
        success=True,
        message="Document deleted successfully"
    )
