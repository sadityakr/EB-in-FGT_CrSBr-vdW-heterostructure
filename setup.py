from setuptools import setup, find_packages

setup(
    name="eb-in-fgt-crsbr",
    version="0.1.0",
    description="Analysis scripts for exchange bias in FGT/CrSBr heterostructures",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "h5py",
    ],
    python_requires=">=3.8",
)
