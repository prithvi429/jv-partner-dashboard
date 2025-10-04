"""
SQLAlchemy ORM models for the JV Dashboard.
Each model represents a table/entity in the DB.
Easy to change: Add fields/relationships here; run Alembic migration.
Imports Base from database.py.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum

# Enums for type safety (easy to extend)
class MarketAlignment(PyEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CompanySize(PyEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class StakeholderRole(PyEnum):
    DECISION_MAKER = "decision-maker"
    INFLUENCER = "influencer"
    TECHNICAL = "technical"

class OutreachResponse(PyEnum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not-interested"
    NO_RESPONSE = "no-response"
    FOLLOW_UP_NEEDED = "follow-up-needed"

class MeetingStatus(PyEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DealStage(PyEnum):
    INTRO = "intro"
    NEGOTIATION = "negotiation"
    MOU = "mou"
    ESTABLISHED = "established"

class ProductTechnology(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    market_alignment = Column(SQLEnum(MarketAlignment))
    manufacturing_suitability = Column(SQLEnum(MarketAlignment))
    revenue_potential = Column(String(100))
    status = Column(String(50), default="research")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (easy to query linked data)
    companies = relationship("TargetCompany", back_populates="product")

class TargetCompany(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    product_technology_id = Column(Integer, ForeignKey("products.id"))
    industry = Column(String(255))
    size = Column(SQLEnum(CompanySize), default=CompanySize.MEDIUM)
    revenue = Column(String(100))
    contact_info = Column(String(255))
    status = Column(String(50), default="identified")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("ProductTechnology", back_populates="companies")
    stakeholders = relationship("Stakeholder", back_populates="company")

class Stakeholder(Base):
    __tablename__ = "stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    email = Column(String(255))
    phone = Column(String(100))
    role = Column(SQLEnum(StakeholderRole), default=StakeholderRole.DECISION_MAKER)
    status = Column(String(50), default="identified")
    linkedin_data = Column(Text)  # JSON string from Proxycurl
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("TargetCompany", back_populates="stakeholders")
    outreaches = relationship("Outreach", back_populates="stakeholder")

class Outreach(Base):
    __tablename__ = "outreaches"
    
    id = Column(Integer, primary_key=True, index=True)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"))
    date = Column(DateTime, default=datetime.utcnow)
    message = Column(Text, nullable=False)
    response = Column(SQLEnum(OutreachResponse), default=OutreachResponse.NO_RESPONSE)
    notes = Column(Text)
    follow_up_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stakeholder = relationship("Stakeholder", back_populates="outreaches")
    meetings = relationship("Meeting", back_populates="outreach")

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    outreach_id = Column(Integer, ForeignKey("outreaches.id"))
    scheduled_date = Column(DateTime)
    participants = Column(String(255))
    agenda = Column(Text)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    outreach = relationship("Outreach", back_populates="meetings")
    deals = relationship("Deal", back_populates="meeting")

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    stage = Column(SQLEnum(DealStage), default=DealStage.INTRO)
    notes = Column(Text)
    docs = Column(Text)  # JSON list of file paths/URLs
    assigned_to = Column(String(255))  # User ID/email for collaboration
    assigned_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="deals")