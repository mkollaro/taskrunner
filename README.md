# TaskRunner

Execute a certain sequence of tasks and later their cleanups. It is useful for
running tasks with many varying configurations. It doesn't have any
dependencies, just the standard library.

```python
# file examples/simple.py
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
```

    $ bin/taskrunner examples/simple.py pipeline
    INFO:taskrunner.main:=========== run task1 ===========
    hello world
    INFO:taskrunner.main:=========== run task2 ===========
    hello again
    INFO:taskrunner.main:--------- cleanup task2 ---------
    :)
    INFO:taskrunner.main:--------- cleanup task1 ---------
    goodbye

### How it works

The pipeline is a list of task configurations, which are normal Python
dictionaries with the special item `'task':ExampleTask`. It goes trough the
list and for each task, it instantiates `ExampleTask` with the rest of the
dictionary content as parameters. Then it executes `ExampleTask.run()` for all
of the tasks. After it passes trough the whole list, it goes trough it in
reverse order and executes `ExampleTask.cleanup()` for each item. The tasks can
write into `context` and the content of it will be passed to the next task.

### Usage

You can specify the pipeline directly as arguments:

    $ bin/taskrunner examples/simple.py task1 task2

Or you can combine multiple pipelines, which will run all the tasks from each
pipeline:

    $ bin/taskrunner examples/simple.py pipeline another_task_pipeline

Or even combine pipelines and tasks (this will run *task2* twice):

    $ bin/taskrunner examples/simple.py pipeline task2

To use the tool as a library, you can directly use `execute`:

```python
taskrunner.execute([task1, task2])
```

#### Taking control of the cleanup execution

Sometimes you want to only execute the `run()` part of the tasks, debug
something and only run the cleanups after you are done. To skip the cleanups,
you can do:

    $ bin/taskrunner examples/simple.py pipeline --cleanup=never

To run the cleanups only:

    $ bin/taskrunner examples/simple.py pipeline --cleanup=pronto

You can also use the options `--cleanup=on_success` or `--cleanup=on_failure`,
which will get executed based on how the `run` turned out.

Don't forget to make the cleanups independent of the runs, otherwise this won't
work.

#### Exception and signal handling

When an exception occurs in the task run, its traceback is logged and it jumps
right into the cleanups. However, it doesn't clean up the tasks that didn't run
(but it does clean up the task which failed and got only partially executed).

If you get an exception during some cleanup, the traceback is logged but
execution continues with the next task's cleanup.

The list of errors gets logged again after everything else finishes, in the
order they happened.

If you terminate the run using `ctrl-c` (also known as *SIGINT*), it will go
straight to the cleanups. Sending the termination signal again will stop it
completely. This works for the *SIGTERM* signal too.

#### The name of a task

By default, the name of a task is the class name. To have more readable logs,
you can specify the keyword `name` in the task configuration.

#### Redefining the configuration trough CLI arguments

Sometimes you want to run a sequence of tasks with some changes in their
configuration, but don't want to change the files. You can redefine it using
the parameter `-D`.

    $ bin/taskrunner examples/simple.py pipeline -D task1.msg=ping

It can't contain contain any spaces, has to be in the exact format of
'varname.keyname=newvalue', where 'varname' is a dictionary in the Python file
you're executing. It doesn't support redefinitions on other levels (e.g.
changing the value of a dictionary in a dictionary).  You can use it multiple
times. It gets redefined right before the tasks get run.

### Best practices for writing tasks and their configurations
* don't make the `cleanup` method dependent on `run`, because with the
  option `--cleanup=pronto`, the `run` method won't get executed
* don't assume that the `run` got executed completely
* put the tasks into a separate file, which will be imported in the file with
  the task configurations
* use the minimum of Python features in the task configuration files (which are
  just `.py` files), variable definitions and if conditions are usually
  sufficient

### Ideas

* support parallel run of tasks by using some special
  `parallel([taskA, taskB])` wrapper
* what if the content of the configuration dictionary depends on the result of
  some other, previously running task? Maybe `eval` could help, e.g.
  `eval("context['some-result']")`, but that is of course quite dangerous
