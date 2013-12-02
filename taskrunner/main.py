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
import sys
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


def execute(pipeline, cleanup="yes"):
    """For each task in pipeline, execute its run method, later the cleanup.

    :param pipeline: list of task configurations, which are dictionaries with
        the special item 'task':TaskClass, which will be instatiated with the
        rest of the dictionary as parameters
    :param cleanup: can be 'always', 'never', 'pronto', 'on_success',
        'on_failure'
    """
    context = dict()
    LOG.debug("Executing tasks:\n%s", pformat(pipeline))
    tasks = _initialize_tasks(pipeline)

    executed_tasks = tasks
    run_failures = []
    cleanup_failures = []
    if cleanup != 'pronto':
        executed_tasks, run_failures = _run_tasks(tasks, context)

    if (cleanup == 'always' or cleanup == 'pronto'
            or (cleanup == 'on_success' and not run_failures)
            or (cleanup == 'on_failure' and run_failures)):
        cleanup_failures = _cleanup_tasks(executed_tasks, context)

    _log_errors(run_failures, cleanup_failures)
    if run_failures or cleanup_failures:
        sys.exit(1)


def _initialize_tasks(pipeline):
    """Initialize tasks with the configurations as parameters.

    :param pipeline: list of task configurations
    :returns: list of task objects
    """
    tasks = []
    for task_config in pipeline:
        params = copy(task_config)
        params.pop('task')
        task = task_config['task'](**params)
        tasks.append(task)
    return tasks


def _run_tasks(tasks, context):
    """For each task, execute its run() method with give context.

    Log the exception if one gets raised.
    Return immediately if SIGINT or SIGTERM is recieved.

    :param tasks: list of task objects
    :param context: shared variable passed between tasks
    :returns: a pair `(executed_tasks, failures)` is returned. If everything
        went without a problem or if it was terminated by the user, the result
        will equal `(tasks, [])`. If an exception was raised,
        `executed_tasks` will be equal to the part of `tasks` that was already
        run including the failed task. The `failures` will be the list of info
        about the failures.
    """
    executed_tasks = []
    failures = []
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
    except Exception, ex:
        LOG.exception("Caught exception while running '%s'", task)
        failure = {'name': ex.__class__.__name__,
                   'msg': str(ex),
                   'task': str(task)}
        failures.append(failure)
    # restore original signal handler
    signal.signal(signal.SIGTERM, original_sigterm_handler)
    return executed_tasks, failures


def _cleanup_tasks(tasks, context, continue_on_failures=True):
    """In reversed order, execute the cleanup() method for each task.

    :param tasks: list of task objects
    :param context: shared variable to pass into the cleanup
    :param continue_on_failures: if True, go to next cleanup if an error
        occurs
    :returns: list of error descriptions
    """
    tasks_reversed = copy(tasks)
    tasks_reversed.reverse()
    failures = []
    for task in tasks_reversed:
        try:
            LOG.info("--------- cleanup %s ---------", task)
            task.cleanup(context)
        except Exception, ex:
            LOG.exception("Caught exception while running '%s'", task)
            failure = {'name': ex.__class__.__name__,
                       'msg': str(ex),
                       'task': str(task)}
            failures.append(failure)
            if continue_on_failures:
                continue
            else:
                return failures
    return failures


def _log_errors(run_failures, cleanup_failures):
    """Log a shortened description for each error that occured, in order"""
    if run_failures or cleanup_failures:
        LOG.info("========================================================")
        LOG.info("Tasks finished unsuccessfully with the following errors:")
    if run_failures:
        for error in run_failures:
            LOG.error("Exception '%s' in '%s.run': %s",
                      error['name'], error['task'], error['msg'])
    if cleanup_failures:
        for error in cleanup_failures:
            LOG.error("Exception '%s' in '%s.cleanup': %s",
                      error['name'], error['task'], error['msg'])


def _sigterm_handler(signum, stackframe):
    """Raise exception on SIGTERM signal
    """
    if signum == signal.SIGTERM:
        raise SigTermException


class SigTermException(Exception):
    pass
