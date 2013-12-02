import logging
import taskrunner

from examples import simple

LOG = logging.getLogger(__name__)


class AdvancedTask(taskrunner.Task):
    def __init__(self, msg, **kwargs):
        super(AdvancedTask, self).__init__(**kwargs)
        self.msg = msg

    def run(self, context):
        LOG.info(self.msg)
        context['myresult'] = 5

    def cleanup(self, context):
        pass


mytask = {
    'task': AdvancedTask,
    'msg': 'hello world',
}

pipeline = [simple.task1, mytask]
