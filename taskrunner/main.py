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
from copy import copy

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Task(object):
    def __init__(self, **kwargs):
        pass

    def run(self, context):
        pass

    def cleanup(self, context):
        pass


def execute(pipeline):
    # initialize tasks with the configurations as parameters
    tasks = []
    context = dict()
    for task_config in pipeline:
        params = copy(task_config)
        params.pop('task')
        task = task_config['task'](**params)
        tasks.append(task)

    # run the tasks, but jump to cleanup if SIGINT or SIGTERM is recieved
    original_sigterm_handler = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        for task in tasks:
            task.run(context)
    except KeyboardInterrupt:
        LOG.info("Got Ctrl-C during task run, jumping to cleanup")
    except SigTermException:
        LOG.info("Got SIGTERM during task run, jumping to cleanup")
    signal.signal(signal.SIGTERM, original_sigterm_handler)

    # clean up the tasks in reverse order
    tasks_reversed = copy(tasks)
    tasks_reversed.reverse()
    for task in tasks_reversed:
        task.cleanup(context)


def sigterm_handler(signum, stackframe):
    """Raise exception on SIGTERM signal
    """
    if signum == signal.SIGTERM:
        raise SigTermException


class SigTermException(Exception):
    pass
