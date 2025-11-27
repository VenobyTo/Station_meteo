"""Setup configuration for the projet package."""

from setuptools import setup, find_packages

setup(
    name="station-meteo",
    version="0.1.0",
    description="Weather data retrieval, cleaning, and analysis",
    author="Mohamed Amine EL ARJOUNI",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=1.3",
        "pyarrow>=6.0.0",
        "meteostat>=1.7.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "station-meteo=projet.cli:main",
        ],
    },
)
