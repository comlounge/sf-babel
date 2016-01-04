"""
starflyer - babel
=================

Module for providing i18n support for starflyer applications, roughly based on flask-babel (https://github.com/mitsuhiko/flask-babel)

"""
from setuptools import setup


setup(
    name='sf-babel',
    version='1.0',
    url='',
    license='BSD',
    author='Christian Scholz',
    author_email='cs@comlounge.net',
    description='i18n for starflyer',
    long_description=__doc__,
    packages=['sfext',
              'sfext.babel',
             ],
    namespace_packages=['sfext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'starflyer',
        'Babel',
        'pytz',
        'speaklater>=1.2',
        'Jinja2>=2.5'
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
