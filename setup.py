from setuptools import setup, find_packages

setup(
    name='trading_agent',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here, e.g.,
        # 'numpy',
        # 'pandas',
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here, e.g.,
            # 'trading-agent=trading_agent.cli:main',
        ],
    },
    author='Federico Ferdinandi',
    author_email='federico.ferdinandi@gmail.com',
    description='A trading agent package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/trading-agent',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)