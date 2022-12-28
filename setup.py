from setuptools import find_packages
from setuptools import setup

setup(
    name="TinyPilot",
    version="0.0.1",
    url="https://github.com/tiny-pilot/tinypilot",
    author="Michael Lynch",
    description="Use your Raspberry Pi as a browser-based KVM.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "eventlet==0.31.0", "Flask==1.1.1", "Flask-SocketIO==5.0.1",
        "Flask-WTF==0.14.3", "pyyaml==5.4.1"
    ],
    entry_points={"console_scripts": ["tinypilot = app.main:main"]},
)
