#    setup.py:
from setuptools import setup, find_packages

setup(
    name='base_bot',
    version='3.1.1',
    packages=find_packages(),
    install_requires=[
        'python-dotenv>=1.0.0',
        'python-socketio>=5.8.0',
        'langchain-openai>=0.2.0',
        ], #add any dependencies here
)