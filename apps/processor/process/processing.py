

import logging
import random
import time
from faker import Faker


logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__).info("Initializing email processing...")
fake = Faker()

def email_processing(email_data):
    sleep_time = random.randint(1, 3)

    logging.info("Sending email...")
    time.sleep(sleep_time)
    logging.info("Email sent")

    message_id = fake.uuid4()
    return {"message_id": message_id, "status": "success"}


def webhook_processing(webhook_data):
    sleep_time = random.randint(1, 2)
    logging.info("Calling webhook...")
    time.sleep(sleep_time)

    chance = random.randint(1, 100)
    if chance <= 80:
        logging.info("Webhook call successful")
        return {"status": "success"}
    else:
        logging.warning("Webhook call failed")
        raise Exception("Webhook call failed")


def report_processing(report_data):
    sleep_time = random.randint(3, 5)

    logging.info("Generating report...")
    time.sleep(sleep_time)

    report_file = f"{fake.url()}/report_{fake.uuid4()}.pdf"
    return {"report_file": report_file}

def batch_processing(batch_data):
    logging.info("Processing batch job...")

    process_progress = 0
    for _ in batch_data:
        sleep_time = random.random() * 2
        time.sleep(sleep_time)

        process_progress += 1
        progress_percentage = (process_progress / len(batch_data)) * 100
        logging.info(f"Batch job progress: {progress_percentage:.2f}% ({process_progress}/{len(batch_data)}) items processed.")

    logging.info("Batch job completed.")
    summary = {"summary": f"Processed {len(batch_data)} items in batch job."}
    return summary