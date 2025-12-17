# backend/app/models/database_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """
    Main document table storing uploaded files and their metadata
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, jpg, png
    file_size = Column(Integer)  # bytes

    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed

    # OCR data
    ocr_text = Column(Text)
    ocr_completed_at = Column(DateTime)

    # Classification
    document_type = Column(String(50))  # invoice, receipt, purchase_order, etc.
    classification_confidence = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    extraction = relationship("Extraction", back_populates="document", uselist=False, cascade="all, delete-orphan")
    line_items = relationship("LineItem", back_populates="document", cascade="all, delete-orphan")


class Extraction(Base):
    """
    Extracted structured data from documents
    """
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Invoice/Receipt fields
    invoice_number = Column(String(100))
    invoice_date = Column(String(50))
    due_date = Column(String(50))

    # Vendor/Merchant info
    vendor_name = Column(String(255))
    vendor_address = Column(Text)

    # Customer info
    customer_name = Column(String(255))
    customer_number = Column(String(100))
    customer_address = Column(Text)

    # Financial data
    subtotal_amount = Column(Float)
    tax_amount = Column(Float)
    vat_amount = Column(Float)
    total_amount = Column(Float)
    currency = Column(String(10))

    # Additional fields
    payment_method = Column(String(50))
    payment_terms = Column(Text)

    # PO specific
    po_number = Column(String(100))

    # Summary
    summary = Column(Text)

    # Raw extraction (full JSON from Gemini)
    raw_extraction = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extraction")


class LineItem(Base):
    """
    Individual line items from invoices/receipts/POs
    """
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    description = Column(Text)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)

    # Additional fields
    sku = Column(String(100))
    unit = Column(String(50))
    tax_rate = Column(Float)

    # Metadata
    line_number = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="line_items")


class ProcessingLog(Base):
    """
    Audit log for all processing steps
    """
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))

    step = Column(String(50))  # upload, ocr, classify, extract
    status = Column(String(50))  # started, completed, failed
    message = Column(Text)
    error = Column(Text)

    # Performance metrics
    duration_ms = Column(Integer)
    cache_hit = Column(Integer, default=0)  # 0=miss, 1=hit

    timestamp = Column(DateTime, default=datetime.utcnow)