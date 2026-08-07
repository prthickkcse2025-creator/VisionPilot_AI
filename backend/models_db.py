import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="operator")  # admin, operator, viewer
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history_records = relationship("ProcessingHistory", back_populates="image")

class ProcessingHistory(Base):
    __tablename__ = "processing_history"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    status = Column(String, nullable=False)  # pending, success, failed
    optimization_decision = Column(String, nullable=True)  # e.g., "HDR + Straighten", "Skip HDR"
    straighten_angle = Column(Float, default=0.0)
    confidence_score = Column(Float, default=1.0)
    
    # Timing fields in milliseconds
    total_time_ms = Column(Float, default=0.0)
    straightener_time_ms = Column(Float, default=0.0)
    hdr_time_ms = Column(Float, default=0.0)
    quality_time_ms = Column(Float, default=0.0)
    detection_time_ms = Column(Float, default=0.0)
    ocr_time_ms = Column(Float, default=0.0)
    packaging_time_ms = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    image = relationship("Image", back_populates="history_records")
    ocr_results = relationship("OCRResult", back_populates="history")
    detection_results = relationship("DetectionResult", back_populates="history")
    packaging_results = relationship("PackagingResult", back_populates="history")
    pipeline_logs = relationship("PipelineLog", back_populates="history")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("processing_history.id"), nullable=False)
    detected_text = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    # Bounding box coords in normalized format
    box_x = Column(Float, nullable=True)
    box_y = Column(Float, nullable=True)
    box_w = Column(Float, nullable=True)
    box_h = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history = relationship("ProcessingHistory", back_populates="ocr_results")

class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("processing_history.id"), nullable=False)
    class_name = Column(String, nullable=False)  # e.g. "package", "bottle"
    confidence = Column(Float, nullable=False)
    # Bounding box coords
    box_x = Column(Float, nullable=True)
    box_y = Column(Float, nullable=True)
    box_w = Column(Float, nullable=True)
    box_h = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history = relationship("ProcessingHistory", back_populates="detection_results")

class PackagingResult(Base):
    __tablename__ = "packaging_results"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("processing_history.id"), nullable=False)
    label_present = Column(Boolean, default=True)
    orientation_ok = Column(Boolean, default=True)
    barcode_verified = Column(Boolean, default=True)
    final_status = Column(String, default="PASS")  # PASS / FAIL
    confidence = Column(Float, default=1.0)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history = relationship("ProcessingHistory", back_populates="packaging_results")

class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("processing_history.id"), nullable=True)
    log_level = Column(String, default="INFO")
    message = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    history = relationship("ProcessingHistory", back_populates="pipeline_logs")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    category = Column(String, default="system")
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
