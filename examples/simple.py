import taskrunner


class ExampleTask(taskrunner.Task):
    def __init__(self, msg, clean_msg, **kwargs):
        super(ExampleTask, self).__init__(**kwargs)
        self.msg = msg
        self.clean_msg = clean_msg

    def run(self, context):
        print self.msg

    def cleanup(self, context):
        print self.clean_msg


task1 = {'task': ExampleTask,
         'name': 'task1',
         'msg': 'hello world',
         'clean_msg': 'goodbye'}

task2 = {'task': ExampleTask,
         'name': 'task2',
         'msg': 'hello again',
         'clean_msg': ':)'}

pipeline = [task1, task2]
