from setuptools import setup, find_packages

setup(
    name='shadowraiders',
    version='1.0.0',
    author='Karen Kijima',
    author_email='k.renren0119@gmail.com',
    description='play shadowraiders game with reinforcement learning',
    packages=find_packages(),
    install_requires=[
        'numpy==1.19.5',
        'gym==0.26.2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)