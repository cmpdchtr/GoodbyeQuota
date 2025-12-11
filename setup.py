from setuptools import setup, find_packages

setup(
    name="goodbye_quota",
    version="0.1.0",
    description="A wrapper for Gemini API to handle multiple API keys and rotate them on quota exhaustion.",
    author="@cmpdchtr",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
    ],
)
