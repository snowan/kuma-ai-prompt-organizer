from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ai-prompt-manager",
    version="0.1.0",
    packages=find_packages(include=['app*']),
    install_requires=read_requirements(),
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A web application for managing AI prompts with categories and tags",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-prompt-manager",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'ai-prompt-manager=main:main',
        ],
    },
)
