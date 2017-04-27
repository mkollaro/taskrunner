from setuptools import setup
try:
    # pypi doesn't support the .md format
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(
    name='taskrunner',
    version='0.3.0',
    author='Martina Kollarova',
    author_email='mkollaro@gmail.com',
    url='http://pypi.python.org/pypi/taskrunner/',
    packages=['taskrunner'],
    license='Apache License, Version 2.0',
    scripts=['bin/taskrunner'],
    description='Execute a certain sequence of tasks and later their'
                ' cleanups in reverse order.',
    long_description=long_description,
    tests_require=['nose'],
)
