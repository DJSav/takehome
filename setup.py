from setuptools import setup


setup(
    name='takehome',
    version='1.0',
    py_modules=['index_proj'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        index=index_proj:index
    ''',
)
