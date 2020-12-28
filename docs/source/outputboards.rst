Appendix: Preparing an Output Board
===================================

.. contents:: Contents
   :local:
   :depth: 3

There are three ways to prepare a trigger-output board:

1. Write a sketch to Arduino UNO (or its clone)
2. Write a sketch to Arduino Leonardo (or its clone)
3. (Optimal) Flash the ``Arduino-fasteventserver`` kernel to Arduino UNO (or its clone)

Before starting, make sure about :doc:`the path to your Arduino board <paths>`.

Writing a sketch to Arduino UNO
-------------------------------

Although this may add a 1-2 ms overhead to the output latency, this is probably the simplest way. Any UNO clone (including Nano clones) should work.

1. Find the ``SimpleArduinoOutput`` sketch from the ``libraries`` directory of the repository.
2. Using the Arduino app, compile and write the sketch to your UNO clone.

To use this type of output boards, select ``uno`` as the "driver type" of FastEventServer.

By default, the trigger output comes out of the pin ``GPIO13`` (LED).


Writing a sketch to Arduino Leonardo
------------------------------------

Leonardo- and Micro- clones fall into this category. Boards of this type may also add a 1-2 ms overhead to the output latency.

1. Find the ``SimpleArduinoOutput`` sketch from the ``libraries`` directory of the repository.
2. Using the Arduino app, compile and write the sketch to your Leonardo clone.

To use this type of output boards, select ``leonardo`` as the "driver type" of FastEventServer.

By default, the trigger output comes out of the pin ``GPIO13`` (LED).

Flashing Arduino-fasteventoutput to a UNO clone
------------------------------------------------

This method makes use of the `arduino-fasteventtrigger`_ project.

By using this method, the trigger-output latency will go down to the sub-millisecond order. Nevertheless, it takes some additional procedures to follow.

.. caution::
   ``arduino-fasteventoutput``, in reality, will **only make use of the serial-to-USB conversion tip on the UNO (i.e. ATmega16U2)**.
   This means:

   - Make sure that your UNO clone has the ATmega16U2 as its converter chip.
   - Other USB-based boards that uses the ATmega16U2 chip *may* work (not recommended nor supported).

To flash a kernel to ATmega16U2, we need to turn the chip into the "Device Firmware Update" (DFU) mode, by which you can send the kernel data directly through the USB cable. You can learn more about the DFU mode `here on the official website <https://www.arduino.cc/en/Hacking/DFUProgramming8U2>`_.

First find the ``Arduino-fasteventoutput.hex`` binary from the ``libraries`` directory of the Pose-Trigger repository. The rest of the procedures are as follows:

1. **Install ``dfu-programmer``**: e.g. on Ubuntu, it can be simply done by running ``sudo apt-get dfu-programmer``.
2. **Put the UNO board into the DFU mode, being left connected to the computer**:

    for UNO rev. 2 and later, the board can be put into the DFU mode by briefly connecting the `RESET` and `GND` pins of the 6-pin header connected to the ATmega16U2 chip. The image below shows the positions of the `RESET` and `GND` pins (and their 6-pin header):

    .. figure:: ../../resources/UNO-dfu.png
        :scale: 30%

        The location of the ``RESET`` and the ``GND`` pins

    .. note::

    	After going into the DFU mode, **the path to the UNO device will disappear from the "/dev" directory** (so don't worry about it).

3. **Erase the previous kernel**: run ``sudo dfu-programmer atmega16u2 erase``.
4. **Write out our kernel**: run ``sudo dfu-programmer atmega16u2 flash Arduino-fasteventoutput.hex``.
5. **Reset (re-boot) the UNO**: run ``sudo dfu-programmer atmega16u2 reset``.

    Check that the UNO board appears again under the ``/dev`` directory.

.. note::

	by writing ``fasteventoutput`` to the Arduino board, **it cannot be used any more as an Arduino**.

    In case you want to "resume" the Arduino functionalities, write back the `official Arduino firmware <https://github.com/arduino/ArduinoCore-avr/tree/master/firmwares/atmegaxxu2>`_ using ``dfu-programmer`` again by following the same procedures.

.. _arduino-fasteventtrigger: https://doi.org/10.5281/zenodo.3515998
