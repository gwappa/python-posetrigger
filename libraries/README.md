# Libraries for Pose-Trigger output

## Arduino-fasteventoutput

This is a program to be uploaded to your Arduino UNO so that it can be used as a fast-output board. Prerequisites and installation procedures are as follows.

### Prerequisite: Arduino UNO

`fasteventoutput` requires an Arduino UNO single-board computer (rev. 2 or later), or one of its "clones".

**NOTE**: in reality, it only engages the usb-to-serial converter chip (ATmega16U2) on the UNO, i.e. it does _not_ use the ATmega328P (the main microcontroller of UNO). Make sure that your clone uses ATmega16U2 as the usb-to-serial converter.

### Prerequisite: dfu-programmer

Programming the AVR microcontroller (those utilized by Arduino's) over the USB cable uses the special, **"Device Firmware Update" (DFU) mode** of the chip. Although the AVR program itself is provided here, you need to install another application that takes care of writing to a device in the DFU mode.

There is a free software called [dfu-programmer](http://dfu-programmer.github.io/) that exactly does this job. Install it to any of your Linux computers. The package manager on your computer can take care of all the necessary installation procedures:

- (On linux) run e.g. `sudo apt-get dfu-programmer` (depending on your distribution, the command `apt-get` can be `aptitude`, `pacman` etc.).

### Writing `fasteventoutput` to the Arduino board

All the procedures are described in details in the [official Arduino website](https://www.arduino.cc/en/Hacking/DFUProgramming8U2), but the essence is stated in brief here, too:

1. Plug in your UNO board to your Linux PC (where `dfu-programmer` is installed).
2. Open this `libary` directory in Terminal.
3. Check that the UNO is recognized by the PC:
   - Plug in and out the UNO board, and run `ls -l /dev | grep ttyACM` every time.
   - There should be a name (e.g. `ttyACM0`) that shows up only when the UNO is connected to the PC. This name corresponds to the name of the UNO.
4. Turn the UNO into the DFU mode, by connecting the `RESET` and `GND` pins briefly using a piece of wire (see the image below).
   - Do _not_ disconnect the UNO and the PC hereafter.
   - Make sure that the device disappears from the list shown by  `ls -l /dev | grep ttyACM` , even when the UNO board is plugged in.
5. Erase the existing program by running `sudo dfu-programmer atmega16u2 erase`
6. Write `fasteventoutput` to the UNO by running `sudo dfu-programmer atmega16u2 flash Arduino-fasteventoutput.hex`
7. Reset (re-boot) the UNO by running `sudo dfu-programmer atmega16u2 reset`
8. Check that the UNO board is recognized by the PC again.
   - use  `ls -l /dev | grep ttyACM`  again.
   - The device will show up only after un-plugging the board and plugging it in again.

**NOTE**: by writing `fasteventoutput` to the Arduino board, it cannot be used any more as an Arduino. In case you want to "resume" the Arduino functionalities, write back the [official Arduino firmware](https://github.com/arduino/ArduinoCore-avr/tree/master/firmwares/atmegaxxu2) using `dfu-programmer` again by following the same procedures. 

### Testing the board

(TODO)



## FastEventServer

(TODO)