from celery import Celery
from celery.schedules import crontab
from app import create_app
from config import Config

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    
    celery.conf.beat_schedule = {
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0),
        },
        'monthly-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(0, 0, day_of_month='1'),
        }
    }
    celery.conf.timezone = 'UTC'

    return celery

flask_app = create_app()
celery_app = make_celery(flask_app)

import tasks
