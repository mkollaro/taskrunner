from distutils.core import setup

setup(
    name='taskrunner',
    version='0.0.1',
    author='Martina Kollarova',
    author_email='mkollaro@gmail.com',
    url='http://pypi.python.org/pypi/taskrunner/',
    packages=['taskrunner'],
    license='LICENSE',
    scripts=['bin/taskrunner'],
    description='Execute a certain sequence of tasks and later their'
                ' cleanups in reverse order.',
    long_description=open('README.md').read(),
    install_requires=[],
)
