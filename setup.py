from setuptools import setup

with open('README.rst') as desc:
    long_description = desc.read()

setup(
    name="pimgupme",
    version="0.31.3",
    author="bubonic & theirix",
    author_email="bubonic@tessellations.net, theirix@gmail.com",
    description=(
        "PTPImg uploader, handles local files and URLs, from the commandline with thumbnail and bbcode support"),
    long_description=long_description,
    license="BSD",
    keywords="image uploader",
    url="https://github.com/bubonic/pimgupme",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    py_modules=['pimgupme'],
    entry_points={
        'console_scripts': [
            'pimgupme = pimgupme:main',
        ],
    },
    install_requires=[
        'requests',
    ],
    python_requires=">=3.3"
)
