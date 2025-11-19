"""
Setup pour installer auto_debug comme commande système
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Lire les dépendances depuis requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        install_requires = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

# Ajouter requests qui est utilisé dans auto_debugger.py
if not any('requests' in req for req in install_requires):
    install_requires.append('requests>=2.31.0')

setup(
    name="auto-debug",
    version="1.0.0",
    description="Débogage intelligent Python avec Groq AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="The commiteer - The prompter - The env pusher",
    author_email="prompter.committer@env.pusher",
    url="https://github.com/AbdessamadTzn/auto_debugger",
    packages=find_packages(),
    py_modules=['auto_debugger', 'config', 'executor', 'llm_analyzer', 'patcher'],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'auto_debug=auto_debugger:main',
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
        "Programming Language :: Python :: 3.12",
    ],
    python_requires='>=3.8',
    keywords='debug debugger ai groq python automation',
    include_package_data=True,
)

