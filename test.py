from flask import Flask
import datetime
from flask_apscheduler import APScheduler

aps = APScheduler()
app = Flask(__name__)


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'test:task',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 1
        }
    ]
    SCHEDULER_API_ENABLED = True


def task(a, b):
    print(str(datetime.datetime.now()) + ' execute task ' + '{}+{}={}'.format(a, b, a + b))


app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.run(port=8000)
