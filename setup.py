from setuptools import find_packages, setup

setup(
    name='appmar2',
    version='2.0.0',
    packages=find_packages(),
    install_requires=['pygubu>=0.10.1', 'pandas>=1.0.3', 'numpy>=1.18.1', 'xarray>=0.15.1',
                      'matplotlib>=3.1.3', 'seaborn>=0.10.0', 'statsmodels>=0.11.0', 'Cartopy>=0.17.0'],
    python_requires='>=3.7',
    include_package_data=True,
    entry_points={'console_scripts': ['appmar2 = appmar2.__main__:main']},
    author='CEMAN',
    description='Python program for marine climate analysis.',
    keywords='marine climate',
    url='https://github.com/cemanetwork/appmar2',
    classifiers=['License :: OSI Approved :: MIT License']
)