Installation
=============

.. contents:: Contents
   :local:
   :depth: 3

.. _requirements:

System requirements
--------------------

.. _minimum requirements:

Minimum installation requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have the followings, you can perform acquisition of video frames *without body-part estimation or trigger generation*:

* **A linux computer** (tested on `Ubuntu 18.04 LTS`_)
* An installation of **Python, version >=3.4**. We recommend installing the following libraries using e.g. `Anaconda`_:

    * NumPy
    * Matplotlib
    * python-opencv
    * PyQt (required for pyqtgraph)
    * `pyqtgraph`_ (through ``pip``, instead of through ``conda``)

* **a 16-bit monochrome video camera** from `ImagingSource`_ (e.g. refer to the :ref:`Reference setup`).

.. note:: Other Video4Linux2-compliant cameras should also work with a few adjustments in the code, but will require some efforts.

Requirements for on-line position estimation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The on-line position-estimation feature requires the followings in your environment:

* An installation of `DeepLabCut`_ (any versions after 1.11 should work).
* For a faster working of DeepLabCut, **NVIDIA graphics board with a large amount of RAM** is required.

.. note:: For example, running DeepLabCut on ResNet-50 requires ~10.6 GB of RAM,
    so we use `GeForce RTX 2080 Ti`_ that has 11 GB on-board RAM (refer to the :ref:`Reference setup`).

Requirements for trigger-output generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the pose-estimation feature, the trigger-output feature requires the followings:

* The `FastEventServer`_ **server program**.
* An `Arduino UNO`_ or its clone, being flashed with the `arduino-fasteventtrigger`_ program.

For installation of the softwares, refer to the README file in the "libraries" directory of the repository.

.. caution::
    ``arduino-fasteventtrigger``, in reality, will **only make use of the serial-to-USB conversion tip on the UNO (i.e. `ATmega16U2`_)**.
    This means:

    - Make sure that your UNO clone has the ATmega16U2 as its converter chip.
    - Other USB-based boards that uses the ATmega16U2 chip *may* work (not recommended nor supported).

.. _Reference setup:

Reference setup specifications
-------------------------------

We develop and test Pose-Trigger in the following environment:

Hardware
^^^^^^^^^

.. table:: Reference setup hardware specifications

    ============= ==============================================================
    Part name     Model type
    ============= ==============================================================
    CPU           3.7 GHz Core i7-9700K
    RAM           64 GB DDR4-3200
    GPU           NVIDIA GeForce RTX 2080 Ti (11 GB RAM)
    Camera        ImagingSource DMK 37BUX287
    Output board  Arduino UNO, rev. 2 (clone), with `arduino-fasteventtrigger`_
    ============= ==============================================================

Software
^^^^^^^^^

.. table:: Reference setup software environment

    ================== ====================================================
    Software           Specification
    ================== ====================================================
    Operating system   Ubuntu 18.04 LTS
    Python environment Anaconda3, Python 3.7.7
    CUDA Toolkit       version 10.1 (through `conda`)
    Tensorflow         version 1.13.1 (`tensorflow-gpu` package of `conda`)
    DeepLabCut         version 2.1.3
    NumPy              version 1.19.1 (through `conda`)
    ================== ====================================================


Install procedures
-------------------

Install all the python packages in your DeepLabCut environment.

1. If you need DeepLabCut, install it first.
2. Install the libraries specified in the `minimum requirements`_ section.
3. Install ``timedcapture``: this is the library for video acquisition.
4. Install the ``pose-trigger`` module.
5. You can install ``FastEventServer`` and connect Arduino at any moment during the procedure (please refer to the README file in the "libraries" directory of the repository).

.. note::
    Upon the public release of Pose-Trigger in the future, both ``timedcapture`` and ``pose-trigger`` packages will be made available in PyPI. One will be able to install these packages through the ``pip install`` command.

    Before this becomes the case, below are the procedures:

    1. Clone the repository.
    2. Open the cloned repository directory in Terminal.
    3. Run ``pip install .`` on Terminal.

.. _Ubuntu 18.04 LTS: https://releases.ubuntu.com/18.04.5/
.. _ImagingSource: https://www.theimagingsource.com/
.. _Anaconda: https://www.anaconda.com/
.. _pyqtgraph: http://pyqtgraph.org/
.. _DeepLabCut: http://www.mousemotorlab.org/deeplabcut
.. _GeForce RTX 2080 Ti: https://www.nvidia.com/en-eu/geforce/graphics-cards/rtx-2080-ti/
.. _FastEventServer: https://doi.org/10.5281/zenodo.3843623
.. _arduino-fasteventtrigger: https://doi.org/10.5281/zenodo.3515998
.. _Arduino UNO: https://store.arduino.cc/arduino-uno-rev3
.. _ATmega16U2: https://www.microchip.com/wwwproducts/en/ATmega16U2
