from setuptools import setup

setup(
    name='taskrunner',
    version='0.1',
    author='Martina Kollarova',
    author_email='mkollaro@gmail.com',
    url='http://pypi.python.org/pypi/taskrunner/',
    packages=['taskrunner'],
    license='Apache License, Version 2.0',
    scripts=['bin/taskrunner'],
    description='Execute a certain sequence of tasks and later their'
                ' cleanups in reverse order.',
)
