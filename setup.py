from setuptools import setup, find_packages

setup(
    name="filo-0.5",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.0",
        "Flask-CORS>=4.0.0",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "reportlab>=4.0.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Werkzeug>=2.3.0",
    ],
    python_requires=">=3.8",
) 