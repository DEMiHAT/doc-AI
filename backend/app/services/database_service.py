# backend/app/services/database_service.py

from sqlalchemy.orm import Session
from app.models.database_models import Document, Extraction, LineItem, ProcessingLog
from datetime import datetime
from typing import Optional, List, Dict, Any


class DatabaseService:
    """
    Service layer for database operations
    """

    @staticmethod
    def create_document(db: Session, file_id: str, filename: str, file_type: str = None,
                        file_size: int = None) -> Document:
        """
        Create a new document record
        """
        doc = Document(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            status="uploaded"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_document_by_file_id(db: Session, file_id: str) -> Optional[Document]:
        """
        Get document by file_id
        """
        return db.query(Document).filter(Document.file_id == file_id).first()

    @staticmethod
    def update_document_status(db: Session, file_id: str, status: str):
        """
        Update document processing status
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if doc:
            doc.status = status
            doc.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def save_ocr_result(db: Session, file_id: str, ocr_text: str):
        """
        Save OCR text to document
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if doc:
            doc.ocr_text = ocr_text
            doc.ocr_completed_at = datetime.utcnow()
            doc.status = "ocr_completed"
            db.commit()

    @staticmethod
    def save_classification(db: Session, file_id: str, document_type: str, confidence: float):
        """
        Save document classification result
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if doc:
            doc.document_type = document_type
            doc.classification_confidence = confidence
            doc.status = "classified"
            db.commit()

    @staticmethod
    def save_extraction(
            db: Session,
            file_id: str,
            extraction_data: Dict[str, Any],
            summary: str = None
    ) -> Extraction:
        """
        Save extraction results
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if not doc:
            raise ValueError(f"Document not found: {file_id}")

        # Delete existing extraction if any
        existing = db.query(Extraction).filter(Extraction.document_id == doc.id).first()
        if existing:
            db.delete(existing)

        # Create new extraction
        extraction = Extraction(
            document_id=doc.id,
            invoice_number=extraction_data.get("invoice_number"),
            invoice_date=extraction_data.get("invoice_date"),
            due_date=extraction_data.get("due_date"),
            vendor_name=extraction_data.get("vendor_name") or extraction_data.get("merchant_name"),
            vendor_address=extraction_data.get("vendor_address") or extraction_data.get("merchant_address"),
            customer_name=extraction_data.get("customer_name"),
            customer_number=extraction_data.get("customer_number"),
            customer_address=extraction_data.get("customer_address"),
            subtotal_amount=extraction_data.get("subtotal_amount") or extraction_data.get("subtotal"),
            tax_amount=extraction_data.get("tax_amount"),
            vat_amount=extraction_data.get("vat_amount"),
            total_amount=extraction_data.get("total_amount"),
            currency=extraction_data.get("currency") or extraction_data.get("currency_code"),
            payment_method=extraction_data.get("payment_method"),
            payment_terms=extraction_data.get("payment_terms"),
            po_number=extraction_data.get("po_number"),
            summary=summary,
            raw_extraction=extraction_data
        )

        db.add(extraction)
        doc.status = "completed"
        db.commit()
        db.refresh(extraction)
        return extraction

    @staticmethod
    def save_line_items(db: Session, file_id: str, line_items: List[Dict[str, Any]]):
        """
        Save line items
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if not doc:
            raise ValueError(f"Document not found: {file_id}")

        # Delete existing line items
        db.query(LineItem).filter(LineItem.document_id == doc.id).delete()

        # Create new line items
        for idx, item in enumerate(line_items):
            line_item = LineItem(
                document_id=doc.id,
                description=item.get("description") or item.get("desc"),
                quantity=item.get("quantity") or item.get("qty"),
                unit_price=item.get("unit_price"),
                total_price=item.get("total_amount") or item.get("total") or item.get("total_price"),
                sku=item.get("sku"),
                unit=item.get("unit"),
                tax_rate=item.get("tax_rate"),
                line_number=idx + 1
            )
            db.add(line_item)

        db.commit()

    @staticmethod
    def log_processing_step(
            db: Session,
            file_id: str,
            step: str,
            status: str,
            message: str = None,
            error: str = None,
            duration_ms: int = None,
            cache_hit: bool = False
    ):
        """
        Log a processing step for audit trail
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()

        log = ProcessingLog(
            document_id=doc.id if doc else None,
            step=step,
            status=status,
            message=message,
            error=error,
            duration_ms=duration_ms,
            cache_hit=1 if cache_hit else 0
        )
        db.add(log)
        db.commit()

    @staticmethod
    def get_all_documents(db: Session, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        Get all documents with pagination
        """
        return db.query(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_documents_by_type(db: Session, document_type: str) -> List[Document]:
        """
        Get documents by type
        """
        return db.query(Document).filter(Document.document_type == document_type).all()

    @staticmethod
    def search_documents(db: Session, query: str) -> List[Document]:
        """
        Search documents by filename or content
        """
        search = f"%{query}%"
        return db.query(Document).filter(
            (Document.filename.ilike(search)) |
            (Document.ocr_text.ilike(search))
        ).all()

    @staticmethod
    def get_document_with_details(db: Session, file_id: str) -> Optional[Dict]:
        """
        Get document with all related data
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if not doc:
            return None

        return {
            "document": doc,
            "extraction": doc.extraction,
            "line_items": doc.line_items
        }

    @staticmethod
    def delete_document(db: Session, file_id: str) -> bool:
        """
        Delete a document and all related data
        """
        doc = db.query(Document).filter(Document.file_id == file_id).first()
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False


# Singleton instance
db_service = DatabaseService()