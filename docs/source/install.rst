Installation
=============

.. contents:: Contents
   :local:
   :depth: 3

Installation
------------

We recommend installing everything through Anaconda3. Make sure your PC satisfies the `requirements`_.

Find the environment file ``posetrigger.yaml`` from the repository, and run the following command in the terminal:

   .. code-block:: Bash

       $ conda env create -f posetrigger.yaml; conda activate posetrigger

You can change the name of the environment by giving the alternative as ``conda env create -n <name> -f posetrigger.yaml``.

.. note::
    Upon the public release of Pose-Trigger in the future, ``timedcapture``, ``dlclib`` and ``pose-trigger`` packages will be made available in PyPI.

To install FastEventServer, refer to :doc:`Appendix <fasteventserver>`.

.. _requirements:

System requirements
-------------------

Before installing Pose-Trigger, make sure you have set up the following hardware:

1. **A linux computer** (tested on `Ubuntu 18.04 LTS`_)
2. **a 16-bit monochrome video camera** from `ImagingSource`_ (e.g. refer to the :ref:`Reference setup`).

    .. note:: Other Video4Linux2-compliant cameras should also work with a few adjustments in the code, but will require some efforts.

3. For a faster working of DeepLabCut, **NVIDIA graphics board with a large amount of RAM** is required.

    .. note:: For example, running DeepLabCut on ResNet-50 requires ~10.6 GB of RAM,
        so we use `GeForce RTX 2080 Ti`_ that has 11 GB on-board RAM (refer to the :ref:`Reference setup`).


Requirements for trigger-output generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the pose-estimation feature, the trigger-output feature requires the followings:

1. The `FastEventServer`_ **server program**.
2. An `Arduino UNO`_ or its clone, being flashed with the `arduino-fasteventtrigger`_ program.

For installation of the softwares, refer to :doc:`Appendix: FastEventServer <fasteventserver>`.

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

.. _Ubuntu 18.04 LTS: https://releases.ubuntu.com/18.04.5/
.. _ImagingSource: https://www.theimagingsource.com/
.. _Anaconda: https://www.anaconda.com/
.. _DeepLabCut: http://www.mousemotorlab.org/deeplabcut
.. _GeForce RTX 2080 Ti: https://www.nvidia.com/en-eu/geforce/graphics-cards/rtx-2080-ti/
.. _FastEventServer: https://doi.org/10.5281/zenodo.3843623
.. _arduino-fasteventtrigger: https://doi.org/10.5281/zenodo.3515998
.. _Arduino UNO: https://store.arduino.cc/arduino-uno-rev3
.. _ATmega16U2: https://www.microchip.com/wwwproducts/en/ATmega16U2
