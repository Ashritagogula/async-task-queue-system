import json
import os
import time
import pika
from sqlalchemy import text
from src.db.database import SessionLocal


def process_task(task_id: str):
    db = SessionLocal()
    try:
        print(f"[Worker] Marking task {task_id} as PROCESSING", flush=True)

        db.execute(
            text("""
                UPDATE tasks
                SET status = 'PROCESSING',
                    updated_at = NOW()
                WHERE id = :id
            """),
            {"id": task_id}
        )
        db.commit()

        # Simulate long processing
        time.sleep(5)

        print(f"[Worker] Marking task {task_id} as COMPLETED", flush=True)

        db.execute(
            text("""
                UPDATE tasks
                SET status = 'COMPLETED',
                    completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = :id
            """),
            {"id": task_id}
        )
        db.commit()

    except Exception:
        db.execute(
            text("""
                UPDATE tasks
                SET status = 'FAILED',
                    updated_at = NOW()
                WHERE id = :id
            """),
            {"id": task_id}
        )
        db.commit()
        raise

    finally:
        db.close()


def callback(ch, method, properties, body):
    message = json.loads(body)
    task_id = message["task_id"]

    print(f"[Worker] Received task {task_id}", flush=True)

    try:
        process_task(task_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[Worker] Finished task {task_id}", flush=True)

    except Exception as e:
        print(f"[Worker] Error processing task {task_id}: {e}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    print("[Worker] Starting worker...", flush=True)

    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER"),
        os.getenv("RABBITMQ_PASSWORD")
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST"),
            credentials=credentials
        )
    )

    channel = connection.channel()

    channel.queue_declare(
        queue="task_queue",
        durable=True
    )

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="task_queue",
        on_message_callback=callback,
        auto_ack=False
    )

    print("[Worker] Waiting for messages...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
