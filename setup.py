import setuptools

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='cumulus-air-sdk', # Replace with your own username
    version='1.0.0',
    author='Mike Robertson',
    author_email='mrobertson@cumulusnetworks.com',
    description='Python SDK for interacting with Cumulus AIR',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/cumulus-consulting/air/cumulus_air_sdk',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.4',
)
