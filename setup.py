"""
Setup pour installer auto_debug comme commande système
"""
from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="auto-debug",
    version="1.0.0",
    description="Débogage intelligent Python avec Grok AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Votre Nom",
    author_email="votre.email@example.com",
    url="https://github.com/votre-username/auto-debug",
    packages=find_packages(),
    py_modules=['config', 'executor', 'ai_agent', 'patcher', 'ui_streamlit', 'cli'],
    install_requires=[
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'auto_debug=cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.8',
    keywords='debug debugger ai grok python automation',
)