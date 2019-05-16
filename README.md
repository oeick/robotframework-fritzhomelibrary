[![Build Status](https://travis-ci.org/oeick/robotframework-fritzhomelibrary.svg?branch=master)](https://travis-ci.org/oeick/robotframework-fritzhomelibrary)

# Robot Framework FritzHome Library

A Robot Framework Library to access the AVM Home Automation HTTP 
Interface.

With this Library Robot Test Cases and Robot Tasks can retrieve 
measured values from and send commands to the DECT Devices
connected to a fritzbox, such as toggle switches or getting 
temperature from radiator control.

See also the file ``example.robot`` for example robot tasks.

## Installation

**Not published on PyPI now**, but when this is done, use:

    $ pip install robotframework-fritzhomelibrary


## Import

Importing this library into a Robot Test Suite or Robot Task:

    | *** Settings ***    |
    | Library             | FritzHome


## Opening and Closing a Session

To use the keywords of this library, first a session must be opened.

    | *** Task *** |
    | Open Session | ${password} | ${user} | ${url} |

User and URL have default values (``admin`` and ``http://fritz.box``)

A connection to the fritzbox is established, and, if authentication 
succeeds, a session is created.
The library handles the technical part (session id, AIN, ...) in the
background.
Devices are identified just by their names, for example:

    | Set Switch State | my first switch | On |

Close the session with the ``Close Session`` keyword.


## Naming Devices

Most device specific keywords of this library take the *name* of the device to identify it.
The name is given over the fritzbox web interface (*Home Network* / *Smart Home* / *All smart home devices*).
It is possible to use spaces, umlauts and special characters 
(for instance you can name your device ``◄▬┼ Übungsgerät :-) ┼▬►``), because both,
Robot Framework and the operatingsystem of the fritzbox seems to be tolerant with such characters.

Internally devices are identified by their AIN. 
If it becomes necessary to use an AIN in a robot test case or robot task, use the keyword ``Get AIN``.


## Temperature Units

The keywords to get the temperature measured by a device will return the value in *Degree Celsius* (°C) by default.
With the ``unit`` parameter it is possible to get the value in *Degree Fahrenheit* (°F) or *Kelvin* (K) instead.
