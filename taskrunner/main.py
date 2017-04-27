#!/usr/bin/env python
#
# Copyright (c) 2013 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import signal
from copy import copy, deepcopy
from pprint import pformat

LOG = logging.getLogger('taskrunner')


class Task(object):
    """Base task from which all other should derive
    """
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif 'name' in kwargs:
            self.name = kwargs['name']
        else:
            self.name = self.__class__.__name__

    def run(self, context):
        pass

    def cleanup(self, context):
        pass

    def __str__(self):
        return self.name


def extend_dict(source_dict, diff=None, deep=False):
    """Return a copy of source_dict, updated with diffs.

    :param diff: dictionary with which source_dict will updated
    :param deepcopy: use deep copy if True, shallow copy if False
    """
    if deep:
        new_dict = deepcopy(source_dict)
    else:
        new_dict = copy(source_dict)

    if diff:
        new_dict.update(diff)
    return new_dict


def execute(pipeline, cleanup='always', context=None):
    """For each task in pipeline, execute its run method, later the cleanup.

    :param pipeline: list of task configurations, which are dictionaries with
        the special item 'task':TaskClass, which will be instatiated with the
        rest of the dictionary as parameters
    :param cleanup: can be 'always', 'never', 'pronto', 'on_success',
        'on_failure'
    :param context: initial context, mainly useful for unit testing
    :returns: the context that was shared between the tasks
    :raises TaskExecutionException: when the run or cleanup fail
    """
    if context is None:
        context = dict()
    context['_taskrunner'] = {'run_failures': [], 'cleanup_failures': []}
    LOG.debug("Executing tasks:\n%s", pformat(pipeline))
    tasks = _initialize_tasks(pipeline)

    executed_tasks = tasks
    if cleanup != 'pronto':
        executed_tasks = _run_tasks(tasks, context)
    run_failures = context['_taskrunner']['run_failures']

    if (cleanup == 'always' or cleanup == 'pronto'
            or (cleanup == 'on_success' and not run_failures)
            or (cleanup == 'on_failure' and run_failures)):
        _cleanup_tasks(executed_tasks, context)
    else:
        LOG.info('Skipping cleanup: cleanup=%s and failures=%s'
                 % (cleanup, run_failures))
    cleanup_failures = context['_taskrunner']['cleanup_failures']

    LOG.debug("Context shared between task at finish:\n%s", context)
    if run_failures or cleanup_failures:
        raise TaskExecutionException(context, "There was one or more errors"
                                     " during task exacution")
    return context


def _initialize_tasks(pipeline):
    """Initialize tasks with the configurations as parameters.

    :param pipeline: list of task configurations
    :returns: list of task objects
    """
    tasks = []
    for task_config in pipeline:
        if not 'task' in task_config:
            raise KeyError('Missing "task" key in %s' % task_config)
        params = copy(task_config)
        params.pop('task')
        try:
            task = task_config['task'](**params)
        except Exception:
            LOG.error('Unable to instantiate task "%s" with params: %s'
                      % (task_config['task'], params))
            raise
        tasks.append(task)
    return tasks


def _run_tasks(tasks, context):
    """For each task, execute its run() method with give context.

    Log the exception if one gets raised.  Return immediately if SIGINT or
    SIGTERM is recieved.  Saves info about failures that happened during task
    run in `context['_taskrunner']['run_failures']`.

    :param tasks: list of task objects
    :param context: shared variable passed between tasks
    :returns: list of executed tasks - if the run went without a problem or if
        it was terminated by the user, the result will equal `tasks`. If an
        exception was raised, `executed_tasks` will be equal to the part of
        `tasks` that was already run including the failed task
    """
    executed_tasks = []
    original_sigterm_handler = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, _sigterm_handler)
    try:
        for task in tasks:
            LOG.info("=========== run %s ===========", task)
            executed_tasks.append(task)
            task.run(context)
    except KeyboardInterrupt:
        LOG.info("Got Ctrl-C during task run, jumping to cleanup")
    except SigTermException:
        LOG.info("Got SIGTERM during task run, jumping to cleanup")
    except Exception as ex:
        LOG.exception("Caught exception while running '%s'", task)
        failure = {'name': ex.__class__.__name__,
                   'msg': str(ex),
                   'task': str(task)}
        context['_taskrunner']['run_failures'].append(failure)
    # restore original signal handler
    signal.signal(signal.SIGTERM, original_sigterm_handler)
    return executed_tasks


def _cleanup_tasks(tasks, context, continue_on_failures=True):
    """In reversed order, execute the cleanup() method for each task.

    Saves info about failures that happened during task cleanups in
    `context['_taskrunner']['cleanup_failures']`.

    :param tasks: list of task objects
    :param context: shared variable to pass into the cleanup
    :param continue_on_failures: if True, go to next cleanup if an error
        occurs
    """
    tasks_reversed = copy(tasks)
    tasks_reversed.reverse()
    for task in tasks_reversed:
        try:
            LOG.info("--------- cleanup %s ---------", task)
            task.cleanup(context)
        except Exception as ex:
            LOG.exception("Caught exception while running '%s'", task)
            failure = {'name': ex.__class__.__name__,
                       'msg': str(ex),
                       'task': str(task)}
            context['_taskrunner']['cleanup_failures'].append(failure)
            if not continue_on_failures:
                return


def _sigterm_handler(signum, stackframe):
    """Raise exception on SIGTERM signal
    """
    if signum == signal.SIGTERM:
        raise SigTermException


class SigTermException(Exception):
    pass


class TaskExecutionException(Exception):
    def __init__(self, context, *args):
        super(TaskExecutionException, self).__init__(*args)
        self.context = context
