from celery import Celery
from kombu import Queue

def create_celery_app(broker_url=None, backend_url=None, task_always_eager=False):
    celery_app = Celery('tasks')

    # Base configuration
    config = {
        'broker_url': broker_url or 'redis://redis:6379/0',
        'result_backend': backend_url or 'redis://redis:6379/0',
        'task_always_eager': task_always_eager,
        'task_queues': (
            Queue('default', routing_key='task.default'),
            Queue('queue_etl', routing_key='task.etl'),
            Queue('queue_eda', routing_key='task.eda'),
            Queue('queue_model', routing_key='task.model'),
            Queue('queue_report', routing_key='task.report'),
        ),
        'task_default_queue': 'default',
        'task_autoretry_for': (Exception,),
        'task_retry_kwargs': {'max_retries': 3, 'countdown': 5},
        'task_time_limit': 7200,
        'task_soft_time_limit': 7000,
    }

    celery_app.conf.update(config)

    return celery_app
