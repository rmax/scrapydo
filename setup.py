import os
from setuptools import setup, find_packages

LONG_DESC = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


setup(
    name='scrapydo',
    version='0.1.0',
    description='Crochet-based blocking API for Scrapy.',
    long_description=LONG_DESC,
    author='Rolando Espinoza La fuente',
    author_email='darkrho@gmail.com',
    url='https://github.com/darkrho/scrapydo',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Scrapy>=1.0.0',
        'crochet>=1.4.0',
        'pygments',
        'six',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
)
