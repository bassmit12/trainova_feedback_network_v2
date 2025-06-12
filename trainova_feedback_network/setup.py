from setuptools import setup, find_packages

setup(
    name='trainova_feedback_network',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A feedback-based weight prediction model using LSTM and various utility functions.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'torch>=1.7.0',
        'numpy>=1.19.0',
        'pandas>=1.1.0',
        'scikit-learn>=0.24.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)