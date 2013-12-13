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

from nose.tools import assert_raises
import taskrunner


class TestExecute():
    def setup(self):
        self.task1 = {'task': ExampleTask,
                      'name': 'task1',
                      'msg': 'hello world',
                      'clean_msg': 'goodbye'}

        self.task2 = {'task': ExampleTask,
                      'name': 'task2',
                      'msg': 'hello again',
                      'clean_msg': ':)'}

    def teardown(self):
        self.task1 = None
        self.task2 = None

    def test_single_task(self):
        # check if both run and cleanup executed and correctly saved context
        context = taskrunner.execute([self.task1])
        name = self.task1['name']
        assert name in context
        assert context[name]['run'] == self.task1['msg']
        assert context[name]['cleanup'] == self.task1['clean_msg']

    def test_two_tasks(self):
        # check if both run and cleanup executed and correctly saved context
        context = taskrunner.execute([self.task1, self.task2])
        name1 = self.task1['name']
        assert name1 in context
        assert context[name1]['run'] == self.task1['msg']
        assert context[name1]['cleanup'] == self.task1['clean_msg']
        name2 = self.task2['name']
        assert name2 in context
        assert context[name2]['run'] == self.task2['msg']
        assert context[name2]['cleanup'] == self.task2['clean_msg']

    def test_correct_order(self):
        # give them the same name, check if the second task overwrote the first
        self.task1['name'] = self.task2['name'] = 'shared_name'
        context = taskrunner.execute([self.task1, self.task2])
        name = self.task1['name']
        assert name in context
        # second task should run later, overwriting the value
        assert context[name]['run'] == self.task2['msg']
        # firt task will cleanup last, overwriting the value
        assert context[name]['cleanup'] == self.task1['clean_msg']

    def test_cleanup_never(self):
        # check that cleanup didn't execute but run() did
        context = taskrunner.execute([self.task1], cleanup='never')
        name = self.task1['name']
        assert name in context
        assert 'cleanup' not in context[name]
        assert context[name]['run'] == self.task1['msg']

    def test_cleanup_pronto(self):
        # check that run didn't execute but cleanup did
        context = taskrunner.execute([self.task1], cleanup='pronto')
        name = self.task1['name']
        assert name in context
        assert 'run' not in context[name]
        assert context[name]['cleanup'] == self.task1['clean_msg']

    def test_cleanup_on_success_when_successful(self):
        # cleanup='on_success', clean up because it succeeded
        context = taskrunner.execute([self.task1], cleanup='on_success')
        name = self.task1['name']
        assert name in context
        assert context[name]['run'] == self.task1['msg']
        assert context[name]['cleanup'] == self.task1['clean_msg']

    def test_cleanup_on_success_when_failed(self):
        # cleanup='on_success', don't clean up because it failed
        self.task1['task'] = FailingRunTask
        context = dict()
        assert_raises(taskrunner.TaskExecutionException, taskrunner.execute,
                      [self.task1], cleanup='on_success', context=context)
        name = self.task1['name']
        assert name not in context

    def test_cleanup_on_failure_when_successful(self):
        # cleanup='on_failure', don't clean up because it succeeded
        context = taskrunner.execute([self.task1], cleanup='on_failure')
        name = self.task1['name']
        assert name in context
        assert context[name]['run'] == self.task1['msg']
        assert 'cleanup' not in context[name]

    def test_cleanup_on_failure_when_failed(self):
        # cleanup='on_failure', clean up because it failed
        self.task1['task'] = FailingRunTask
        context = dict()
        assert_raises(taskrunner.TaskExecutionException, taskrunner.execute,
                      [self.task1], cleanup='on_failure', context=context)
        name = self.task1['name']
        assert name in context
        assert 'run' not in context[name]  # because it failed
        assert context[name]['cleanup'] == self.task1['clean_msg']


############################ HELPER CLASSES ###################################
class ExampleTask(taskrunner.Task):
    """Saves the given strings into context[self.name]"""
    def __init__(self, msg, clean_msg, **kwargs):
        super(ExampleTask, self).__init__(**kwargs)
        self.msg = msg
        self.clean_msg = clean_msg

    def run(self, context):
        context[self.name] = dict()
        context[self.name]['run'] = self.msg

    def cleanup(self, context):
        if not self.name in context:
            context[self.name] = dict()
        context[self.name]['cleanup'] = self.clean_msg


class FailingRunTask(ExampleTask):
    def run(self, context):
        raise Exception


class FailingCleanupTask(ExampleTask):
    def cleanup(self, context):
        raise Exception
