from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GenerationJob, Certificate
from app.schemas import (
    JobCreate,
    JobCreateResponse,
    JobStatusResponse,
    JobCertificatesResponse
)
from app.services.certificate_service import generate_certificate


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post("/", response_model=JobCreateResponse)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    job = GenerationJob(
        event_name=job_data.event_name,
        organization=job_data.organization,
        event_date=job_data.event_date,
        status="PROCESSING",
        total_certificates=len(job_data.recipients),
        successful_certificates=0,
        failed_certificates=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in job_data.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PROCESSING"
        )

        db.add(certificate)
        db.commit()
        db.refresh(certificate)

        try:
            file_path = generate_certificate(
                certificate_id=certificate.id,
                recipient_name=recipient.name,
                event_name=job_data.event_name,
                organization=job_data.organization,
                event_date=job_data.event_date
            )

            certificate.status = "COMPLETED"
            certificate.file_path = file_path

            job.successful_certificates += 1

        except Exception as e:
            certificate.status = "FAILED"
            certificate.error_message = str(e)

            job.failed_certificates += 1

        db.commit()

    if job.failed_certificates == 0:
        job.status = "COMPLETED"
    elif job.successful_certificates > 0:
        job.status = "PARTIAL_FAILURE"
    else:
        job.status = "FAILED"

    db.commit()

    return {
        "job_id": job.id,
        "status": job.status,
        "total_certificates": job.total_certificates,
        "successful_certificates": job.successful_certificates,
        "failed_certificates": job.failed_certificates,
        "message": "Bulk certificate generation completed"
    }


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_certificates": job.total_certificates,
        "successful_certificates": job.successful_certificates,
        "failed_certificates": job.failed_certificates,
        "progress": (
            f"{job.successful_certificates + job.failed_certificates}"
            f"/{job.total_certificates}"
        )
    }


@router.get(
    "/{job_id}/certificates",
    response_model=JobCertificatesResponse
)
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).all()

    return {
        "job_id": job_id,
        "total_certificates": len(certificates),
        "certificates": [
            {
                "id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "file_path": certificate.file_path,
                "error_message": certificate.error_message
            }
            for certificate in certificates
        ]
    }


@router.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Certificate is not available for download"
        )

    file_path = Path(certificate.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )