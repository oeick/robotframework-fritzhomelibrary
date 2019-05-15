*** Settings ***
Documentation    Example for a Robot Task controlling some
...              home automation devices with fritzbox
Library      FritzHome

*** Variables ***
${password}    0000
${user}    robot
${url}    http://192.168.178.1

*** Tasks ***
Switch On
    Open Session    ${password}    username=${user}    url=${url}
    Set Switch State      My Switch    On

Switch Off
    Open Session    ${password}    username=${user}    url=${url}
    Set Switch State      My Switch    Off

Get some infos from my switch
    Open Session    ${password}    username=${user}    url=${url}
    ${name}    Set Variable    My Switch
    ${power}    Get Switch Power    ${name}
    ${energy}   Get Switch Energy   ${name}
    ${t_c}    Get Temperature    ${name}
    ${t_f}    Get Temperature    ${name}    Fahrenheit
    ${t_k}    Get Temperature    ${name}    Kelvin
    log    Power : ${power} mW
    log    Energy: ${energy} Wh
    log    Temp. : ${t_c} °C / ${t_f} °F / ${t_k} K

List of all Devices
    Open Session    ${password}    username=${user}    url=${url}
    ${liste}    Get All Devices
    log    ${liste}

Radiator Control Infos
    Open Session    ${password}    username=${user}    url=${url}
    ${name}    Set Variable    My Radiator Control
    ${t_set}        Get Radiator Control Setpoint    ${name}
    ${t_comfort}    Get Radiator Control Comfort     ${name}
    ${t_eco}        Get Radiator Control Economy     ${name}
    ${t1}           Get Temperature                  ${name}
    log    t        : ${t1}
    log    t_set    : ${t_set}
    log    t_comfort: ${t_comfort}
    log    t_eco    : ${t_eco}
