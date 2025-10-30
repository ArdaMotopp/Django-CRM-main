# setup.py (modernized, simple)
import os
from pathlib import Path
from setuptools import find_packages, setup

ROOT = Path(__file__).parent
readme_path = ROOT / "README.rst"
try:
    long_description = readme_path.read_text(encoding="utf-8")
    long_description_content_type = "text/x-rst"
except FileNotFoundError:
    long_description = ""
    long_description_content_type = "text/plain"

setup(
    name="django-crm",
    version="0.7.0",
    description="An open-source CRM built on the Django framework",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url="https://github.com/MicroPyramid/Django-CRM.git",
    author="Micropyramid",
    author_email="hello@micropyramid.com",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*", "docs", "examples")),
    include_package_data=True,  # include files from MANIFEST.in if present
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    # Keep this empty if you're installing deps from requirements.txt in Docker.
    # If you want pip install . to also pull deps, uncomment and pin versions:
    # install_requires=[
    #     "Django>=3.2,<5.0",
    #     "psycopg2>=2.9",  # or psycopg2-binary for local dev only
    #     "Pillow>=8.0",
    # ],
)

