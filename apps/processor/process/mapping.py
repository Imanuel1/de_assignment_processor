from apps.processor.process.processing import email_processing, webhook_processing, report_processing, batch_processing


process_mapping = {
    "email": email_processing,
    "webhook": webhook_processing,
    "report": report_processing,
    "batch": batch_processing
}

def process_job_by_type(job_type, job_data):
    processing_function = process_mapping.get(job_type)
    if not processing_function:
        raise ValueError(f"Unsupported job type: {job_type}")
    
    return processing_function(job_data)