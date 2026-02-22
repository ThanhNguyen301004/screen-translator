from setuptools import setup, find_packages

setup(
    name='screen_translator',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'keyboard',
        'mss',
        'Pillow',
        'pytesseract',
        'googletrans==4.0.0-rc1',
    ],
    entry_points={
        'console_scripts': [
            'screen_translator = src.main:main',
        ],
    },
)