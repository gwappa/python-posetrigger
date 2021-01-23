#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import setuptools
from posetrigger import VERSION_STR

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pose-trigger',
    version=VERSION_STR,
    description='a python application for real-time, closed-loop application of TTL trigger generation based on the pose of the subject',
    long_description=long_description,
    long_description_content_type="text/asciidoc",
    url='https://github.com/gwappa/python-labvideocapture',
    author='Keisuke Sehara',
    author_email='keisuke.sehara@gmail.com',
    license='MIT',
    python_requires='>=3.7',
    install_requires=['numpy', 'matplotlib', 'opencv-python', 'pyqtgraph',
                      'timedcapture>=0.3.2',],
    extras_require={
        "dlc": ['dlclib>=1.0.3',],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        ],
    packages=setuptools.find_packages(),
    package_data={
        "posetrigger": [ "bin/FastEventServer_linux_*" ]
    },
    entry_points={
        "console_scripts": [
            "pose-trigger=posetrigger:main",
            "posetrigger=posetrigger:main"
        ]
    }
)
