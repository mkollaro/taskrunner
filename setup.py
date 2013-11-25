from distutils.core import setup

setup(
    name='task-executor',
    version='0.0.1',
    author='Martina Kollarova',
    author_email='mkollaro@gmail.com',
    url='http://pypi.python.org/pypi/task-executor/',
    packages=['task-executor'],
    license='LICENSE',
    description='Run a sequence of tasks, then run their cleanups in reverse'
                ' order',
    long_description=open('README.md').read(),
    install_requires=[],
)
