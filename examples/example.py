import taskrunner


class ExampleTask(taskrunner.Task):
    def __init__(self, msg, clean_msg):
        self.msg = msg
        self.clean_msg = clean_msg

    def run(self, context):
        print self.msg

    def cleanup(self, context):
        print self.clean_msg


task1 = {'task': ExampleTask, 'msg': 'hello world', 'clean_msg': 'goodbye'}
task2 = {'task': ExampleTask, 'msg': 'task2', 'clean_msg': 'task2 clean'}

taskrunner.execute([task1, task2])
