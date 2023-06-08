from setuptools import find_packages
from setuptools import setup
from os import path

setup(
    name="ledstate",
    version="0.0.1",
    url="",
    project_urls={},
    license="MIT",
    maintainer="",
    maintainer_email="",
    description="Led state App for Flask",
    long_description="",
    long_description_content_type='text/x-rst',
    classifiers=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.5",
    install_requires=[
        "flask==2.3.2",
        "Werkzeug==2.3.4",
        "Jinja2==3.1.2",
        "itsdangerous==2.1.2",
        "click==8.1.3",
        "python-dotenv==1.0.0",
        "Flask-Babel==3.1.0",
        "reportbro-lib>=3.2.0",
        "SQLAlchemy==2.0.15",
        "requests==2.31.0"
    ],
    entry_points={"console_scripts": ["flask = flask.cli:main"]},
)
