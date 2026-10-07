from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Recipient(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=2)
    organization: str = Field(..., min_length=2)
    event_date: str
    recipients: list[Recipient] = Field(..., min_length=1)


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_name: str
    recipient_email: EmailStr
    status: str
    file_path: str | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_name: str
    organization: str
    event_date: str
    status: str
    total_certificates: int
    successful_certificates: int
    failed_certificates: int
    created_at: datetime
    completed_at: datetime | None = None


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    total_certificates: int
    successful_certificates: int
    failed_certificates: int
    message: str


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    total_certificates: int
    successful_certificates: int
    failed_certificates: int
    progress: str


class JobCertificatesResponse(BaseModel):
    job_id: int
    total_certificates: int
    certificates: list[CertificateResponse]
