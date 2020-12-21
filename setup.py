import setuptools

with open("README.md", "r", encoding="utf-8") as fh:long_description = fh.read()

setuptools.setup(
    name="me-calculator-acollu", # Replace with your own username
    version="0.0.1",
    author="Alberto Collu",
    author_email="author@example.com",
    description="Mortgage calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acollu/me_calculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
