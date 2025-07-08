from setuptools import setup, find_packages

setup(
    name="elevator_system",
    version="1.0.0",
    description="A sophisticated elevator system simulator with zone-based operations",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.104.1',
        'uvicorn>=0.24.0',
        'pydantic>=2.5.2',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'pytest>=7.4.3',
        'rich>=13.7.0'
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
) 