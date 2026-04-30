"""
Setup script pour installation du package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="file-organizer-intelligent",
    version="1.0.0",
    author="AI Senior Developer",
    description="Logiciel de tri et fusion intelligente de fichiers et dossiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/file-organizer",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "PySide6>=6.6.0",
        "python-dotenv>=1.0.0",
        "rapidfuzz>=3.5.0",
        "jellyfish>=1.0.0",
        "python-Levenshtein>=0.23.0",
        "unidecode>=1.3.7",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "structlog>=23.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "pytest-mock>=3.12.0",
            "mypy>=1.7.0",
            "ruff>=0.1.7",
            "black>=23.12.0",
        ],
        "nlp": [
            "spacy>=3.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "file-organizer=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
