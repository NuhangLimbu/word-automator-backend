from setuptools import setup, find_packages

setup(
    name="word-automator-backend",
    version="1.0.0",
    description="AI-powered Word automation backend",
    author="AI Automator",
    packages=find_packages(),
    python_requires=">=3.8,<3.12",
    install_requires=[
        "fastapi>=0.104.0,<0.105.0",
        "uvicorn[standard]>=0.24.0,<0.25.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "pydantic>=2.0.0,<3.0.0",
    ]
)