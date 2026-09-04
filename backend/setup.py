from setuptools import setup, find_packages

setup(
    name="musigo",
    version="0.1.0",
    description="AI-powered music discovery platform with RAG capabilities",
    author="Musigo Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "langchain>=0.0.340",
        "chromadb>=0.4.18",
        "librosa>=0.10.1",
        "sentence-transformers>=2.2.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "music-api=api.main:main",
        ],
    },
)
