from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from . import Base

class FindingStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"

class SecurityFramework(Base):
    """
    Compliance Frameworks (e.g., CIS AWS Foundations, SOC 2, HIPAA)
    """
    __tablename__ = "security_frameworks"

    id = Column(String, primary_key=True)  # e.g., 'cis_aws_1.4.0'
    name = Column(String, nullable=False)  # e.g., 'CIS AWS Foundations Benchmark'
    version = Column(String, nullable=False) # e.g., '1.4.0'
    description = Column(Text)

    controls = relationship("SecurityControl", back_populates="framework", cascade="all, delete-orphan")

class SecurityControl(Base):
    """
    Specific controls within a framework (e.g., CIS 1.1)
    """
    __tablename__ = "security_controls"

    id = Column(String, primary_key=True)  # e.g., 'cis_1.1'
    framework_id = Column(String, ForeignKey("security_frameworks.id"), nullable=False)
    control_code = Column(String, nullable=False) # e.g., '1.1'
    title = Column(String, nullable=False) # e.g., 'Root account access keys disabled'
    description = Column(Text)
    
    framework = relationship("SecurityFramework", back_populates="controls")
    checks = relationship("SecurityCheck", back_populates="control")

class SecurityCheck(Base):
    """
    Technical implementation of a security check.
    Maps to a specific control (usually the primary CIS control).
    """
    __tablename__ = "security_checks"

    id = Column(String, primary_key=True)  # e.g., 'check_iam_root_mfa'
    control_id = Column(String, ForeignKey("security_controls.id"), nullable=True) # Primary control mapping
    name = Column(String, nullable=False)  # Human readable name
    description = Column(Text)
    remediation_steps = Column(Text)
    severity = Column(String) # critical, high, medium, low
    
    control = relationship("SecurityControl", back_populates="checks")
    findings = relationship("SecurityFinding", back_populates="check", cascade="all, delete-orphan")

class SecurityFinding(Base):
    """
    The runtime result of a SecurityCheck.
    """
    __tablename__ = "security_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(String, ForeignKey("security_checks.id"), nullable=False)
    
    resource_id = Column(String, nullable=True)   # AWS Resource ID / ARN
    resource_type = Column(String, nullable=True) # e.g., 'AWS::IAM::User'
    account_id = Column(String, nullable=True)
    region = Column(String, nullable=True)
    
    status = Column(Enum(FindingStatus), nullable=False)
    evidence = Column(JSON)        # Technical proof (e.g., {"mfa_active": false})
    
    first_detected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    check = relationship("SecurityCheck", back_populates="findings")
