"""Setup configuration for tap-facebook."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tap-facebook-engagement',
    version='0.1.0',
    description='Singer tap for Facebook engagement metrics via Graph API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Social Integration Research',
    author_email='research@example.com',
    url='https://github.com/halo-engineering/tap_facebook',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='singer tap facebook engagement analytics hotglue',
    packages=find_packages(exclude=['tests', 'docs']),
    python_requires='>=3.8',
    install_requires=[
        'singer-python==5.13.0',
        'requests==2.31.0',
    ],
    extras_require={
        'dev': [
            'pytest==7.4.0',
            'pytest-cov==4.1.0',
            'black==23.7.0',
            'flake8==6.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'tap-facebook=tap_facebook.tap:main',
        ],
    },
)
