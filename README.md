# Task-executor

Execute a certain sequence of tasks and later their cleanups. It is useful for
running tasks with many varying configurations.

## Basic usage

```python
import task-executor

class ExampleTask(task-executor.Task):
    def __init__(self, msg, clean_msg):
        self.msg = msg
        self.clean_msg = clean_msg

    def run(self, context):
        print self.msg

    def cleanup(self, context):
        print self.clean_msg


task1 = {'task': ExampleTask, 'msg': 'hello world', 'clean_msg': 'goodbye'}
task2 = {'task': ExampleTask, 'msg': 'task2', 'clean_msg': 'task2 clean'}

task-executor.execute([task1, task2])
```

Save that code into `example.py` and run it:

    $ python example.py
    hello world
    task2
    task2 clean
    goodbye


### How it works

It takes a simple list of task configurations, which are normal Python
dictionaries with the special item `'task':ExampleTask`. It goes trough the
list and for each task, it instantiates `ExampleTask` with the rest of the
dictionary content as parameters and then executes `ExampleTask.run()`. After
it passes trough the whole list, it goes trough it in reverse order and
executes `ExampleTask.cleanup()` for each item. The tasks can write into
`context` and the content of it will be passed to the next task.

## Ideas

* create CLI command that would work work similarly as Fabric, it would take a
  list of the task configurations directly
* make it possible to somehow change the configuration of tasks from the CLI
* support parallel run of tasks by using some special
  `parallel([taskA, taskB])` wrapper
* control the cleanups by parameter `cleanup=['always','never','pronto']` or
  perhaps `cleanup=['yes', 'no', 'only']
