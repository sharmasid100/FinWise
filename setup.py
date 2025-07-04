from setuptools import setup, find_packages

setup(
    name="faid",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
        'python-dotenv',
        'flask-login'
    ],
)