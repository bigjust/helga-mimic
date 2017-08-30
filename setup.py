from setuptools import setup, find_packages

version = '0.4.2'

setup(
    name="helga-mimic",
    version=version,
    description=('mimics users or channels'),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='irc bot mimic',
    author='Justin Caratzas',
    author_email='bigjust@lambdaphil.es',
    license='LICENSE',
    packages=find_packages(),
    install_requires = (
        'cobe==2.1.2',
        'helga-alias',
        'helga-oral-history',
        'helga-twitter',
        'markovify==0.6.0',
        'requests',
    ),
    include_package_data=True,
    py_modules=['helga_mimic'],
    zip_safe=True,
    entry_points = dict(
        helga_plugins = [
            'mimic = helga_mimic:MimicPlugin',
        ],
    ),
)
