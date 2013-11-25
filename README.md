# TaskRunner

Execute a certain sequence of tasks and later their cleanups. It is useful for
running tasks with many varying configurations.

## Basic example

```python
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


task1 = {'task': ExampleTask, 'msg': 'hello world', 'clean_msg': 'goodbye'}
task2 = {'task': ExampleTask, 'msg': 'task2', 'clean_msg': 'task2 clean'}

taskrunner.execute([task1, task2])
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
dictionary content as parameters. Then it executes `ExampleTask.run()` for all
of the tasks. After it passes trough the whole list, it goes trough it in
reverse order and executes `ExampleTask.cleanup()` for each item. The tasks can
write into `context` and the content of it will be passed to the next task.

If you terminate the run using `ctrl-c`, it will go straight to the cleanups.
Sending the termination signal again will stop it completely. This works for
the *SIGTERM* signal too.

## Usage

You can find more examples in the `examples/` directory.

### Execution trough the command line

Instead of directly using `taskrunner.execute`, you can replace that line in
`example.py` with a line like this:

    task_pipeline = [task1, task2]

Then you can run it from the CLI like this:

    $ taskrunner example.py task_pipeline

You can specify the pipeline directly:

    $ taskrunner example.py task1 task2

Or you can combine multiple pipelines, which will run all the tasks from each
pipeline:

    $ taskrunner example.py task_pipeline another_task_pipeline

Or even combine pipelines and tasks:

    $ taskrunner example.py task_pipeline task1 another_task_pipeline

### Taking control of the cleanup execution

Sometimes you want to only execute the `run()` part of the tasks, debug
something and only run the cleanups after you are done. To skip the cleanups,
you can do:

    $ taskrunner example.py task_pipeline --cleanup=never

To run the cleanups only:

    $ taskrunner example.py task_pipeline --cleanup=pronto

Don't forget to make the cleanups independent of the runs, otherwise this won't
work.

### The name of a task

By default, the name of a task is the class name. Therefore, if you use

    task1 = {'task': ExampleTask, ...
    task2 = {'task': ExampleTask, ...

they will both show up in the logs as 'ExampleTask'. You probably don't want
this, so you can rename them by adding the 'name' keyword into the task
configuration.

    task1 = {'task': ExampleTask, 'name': 'task1', ...
    task2 = {'task': ExampleTask, 'name': 'task2', ...

#### Redefining the configuration trough CLI arguments

Sometimes you want to run a sequence of tasks with some changes in their
configuration, but don't want to change the files. You can redefine it using
the parameter `-D`.

    $ taskrunner example.py task_pipeline -D ExampleTask.msg="hello again"

However, since both *task1* and *task2* have the name *ExampleTask*, it will get
changed in both of them. You can change it for only one task by renaming it
using the `name` keyword, as described in the previous section. Then you can
use it like this:

    $ taskrunner example.py task_pipeline -D \
      task1.msg="hi :)" \
      task2.msg="go away :("

### Best practices for writing tasks and their configurations
* don't make the `cleanup()` method dependent on `run()`, because with the
  option `--cleanup=pronto`, only the cleanups will be run
* put the tasks into a separate file, which will be imported in the file with
  the task configurations
* use the minimum of Python features in the task configuration files (which are
  just `.py` files), variable definitions and if conditions are usually
  sufficient

## Ideas

* create CLI command that would work work similarly as Fabric, it would take a
  list of the task configurations directly
* make it possible to somehow change the configuration of tasks from the CLI
* support parallel run of tasks by using some special
  `parallel([taskA, taskB])` wrapper
* control the cleanups by parameter `cleanup=['always','never','pronto']` or
  perhaps `cleanup=['yes', 'no', 'only']`
* what if the content of the configuration dictionary depends on the result of
  some other, previously running task? Maybe `eval` could help, e.g.
  `eval("context['some-result']")`, but that is of course quite dangerous
