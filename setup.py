from setuptools import setup, find_packages
import os

name = "presence_analyzer"
version = "0.2.0"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="Presence analyzer",
    long_description=read('README.md'),
    classifiers=[],
    keywords="",
    author="",
    author_email='',
    url='',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Flask',
    ],
    entry_points="""
    [console_scripts]
    flask-ctl = presence_analyzer.script:run

    [paste.app_factory]
    main = presence_analyzer.script:make_app
    debug = presence_analyzer.script:make_debug
    """,
)
