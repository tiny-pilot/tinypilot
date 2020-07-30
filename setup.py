from setuptools import find_packages
from setuptools import setup

setup(
    name="TinyPilot",
    version="0.0.1",
    url="https://github.com/mtlynch/tinypilot",
    author="Michael Lynch",
    description="Use your Raspberry Pi as a browser-based KVM.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["eventlet", "Flask", "Flask-SocketIO", "Flask-WTF"],
    entry_points={"console_scripts": ["tinypilot = app.main:main"]},
)
