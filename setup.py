from setuptools import setup, find_packages

# Read version from __init__.py
with open("nexusflow/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nexusflow",
    version=version,
    description="Dynamic Agent Orchestration Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NexusFlow Team",
    author_email="info@nexusflow.ai",
    url="https://nexusflow.ai",
    packages=find_packages(include=["nexusflow", "nexusflow.*"]),
    include_package_data=True,
    package_data={
        "nexusflow": ["py.typed"],
    },
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.95.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "uvicorn>=0.22.0",
        "langchain>=0.0.267",
        "langchain-core>=0.0.10",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "google-cloud-aiplatform>=1.25.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pytest>=7.3.1",
        "alembic>=1.15.1",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "mypy",
            "pytest",
            "pytest-cov",
            "pre-commit",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
