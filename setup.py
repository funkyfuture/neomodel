import sys

from setuptools import setup, find_packages


if sys.version_info < (3, 4):
    raise RuntimeError('Requires Python 3.4 or later.')


setup(
    name='neomodel',
    version='4.0.dev1',
    description='An object mapper for the neo4j graph database.',
    long_description=open('README.rst').read(),
    author='Robin Edwards',
    author_email='robin.ge@gmail.com',
    zip_safe=True,
    url='http://github.com/robinedwards/neomodel',
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    keywords='graph neo4j ORM OGM',
    scripts=['scripts/neomodel_install_labels', 'scripts/neomodel_remove_labels'],  # TODO entrypoint scripts, after logging
    setup_requires=['pytest-runner'] if any(x in ('pytest', 'test') for x in sys.argv) else [],
    tests_require=['pytest'],
    install_requires=['neo4j-driver==1.5.2', 'pytz>=2016'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
    ])
