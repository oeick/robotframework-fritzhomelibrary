# Robot Framework FritzHome Library

A Robot Framework Library to access the AVM Home Automation HTTP 
Interface.

With this Library Robot Test Cases and Robot Tasks can retrieve 
measured values from and send commands to the DECT Devices
connected to a FRITZ!Box, such as toggle switches or getting 
temperature from thermostatic radiator valve.


## Installation

$ pip install robotframework-fritzhome


## Import

Importing this library into a Robot Test Suite or Robot Task:

    | *** Settings ***    |
    | Library             | FritzHome


## Opening a session

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

