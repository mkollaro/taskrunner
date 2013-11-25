import taskrunner


class ExampleTask(taskrunner.Task):
    def __init__(self, msg, **kwargs):
        super(ExampleTask, self).__init__(**kwargs)
        self.msg = msg

    def run(self, context):
        print context
        context['last_msg'] = self.msg

    def cleanup(self, context):
        pass


task1 = {'task': ExampleTask, 'name': 'task1',
         'msg': 'hello world'}
task2 = {'task': ExampleTask, 'name': 'task2',
         'msg': 'and now for something completely different'}

taskrunner.execute([task1, task2])
