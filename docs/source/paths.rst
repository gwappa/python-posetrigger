Appendix: Checking the paths to your devices
=============================================

.. contents:: Contents
   :local:
   :depth: 3

When using devices like cameras or Arduino boards with applications, it is important that you know your "path" to your device in your PC. The interface to your device will typically appear as a special file in your Linux PC, using which applications can read and write data between the device.

Listing up I/O devices
-----------------------

Typically, files of this type are located in the directory ``/dev``.
You can list up the default interfaces (not only Arduino boards but also for any other I/O interfaces, including cameras) using:

.. code-block:: Bash

    $ ls -l /dev

Here, ``ls`` stands for the command that **l**-i-**s**-ts up the files inside a directory. By adding ``-l`` (a so-called "switch", to tell the command to print the files out in the **l**-ong format), you can list them up in such a way that information about each file is printed on a line.

Focusing on serial devices (like Arduino boards)
-------------------------------------------------

By using the ``grep`` command, you can pick up the files of specific names.

For example, in Ubuntu (and other Debian-based distributions), a typical serial device (like an Arduino board) should have the name starting with ``ttyACM`` (e.g. ``ttyACM0``).
Thus, by running the following command, the console will only show serial devices:

.. code-block:: Bash

    $ ls -l /dev | grep ttyACM

In the above command the ``|`` character is called a "pipe" that connects multiple commands, and redirecting the output of the former command to the input of the latter.
Thus, the ``ls`` command first generates the list of files, and then the ``grep`` command filters the output to show only the lines that contain the characters ``ttyACM``.

If you do not connect any Arduino boards, it is likely that there are not outputs there (i.e. it does not display any files info).

By plugging in and out your Arduino board, and running the above command again and again, one specific path appears and disappears in accordance. This name corresponds to **the path to your Arduino board**.

Normally, the path to a board is consistent across sessions. Thus, when specifying the "output board" for FastEventServer, you can use this path (e.g. ``/dev/ttyACM0``) to select the board of interest.

Focusing on cameras
--------------------

Similarly, a (video) camera typically have a path starting with ``video`` e.g. ``/dev/video0``. You can therefore find the path to your camera by running the following command:

.. code-block:: Bash

    $ ls -l /dev | grep video

Typically, a single camera has multiple files corresponding to e.g. video and still-frame capture interfaces. You may need to check which file corresponds to the video interface of your camera (for ImagingSource cameras, it is ``/dev/video0``).
