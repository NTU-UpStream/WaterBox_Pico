# Here documented some AT command that I feel like are useful.

## Initialization


## CH4 General 
This chapter have some system command.  
Like serial number, manufacturer, SIM card info etc.  

- AT+CCID: ICCID of SIM card.

## CH5 Equipment Control  

- AT+CPWROFF: Power off the module safely

- AT+CFUN: Some useful module functionality  
    Including fast poweroff.
    15: Silent reset (will reboot).

- AT+CSGT: Greeting text after boot.

## CH7 Network Configuration  

- AT+UMNOPROF: Set MNO profile  
    Module are *SUPPOSED* to work with a profile.  
    Normally it is set to 0 (undefined).

- AT+CGATT: Check if module is attached to network  
    0: detached  
    1: attached  

- AT+CGDCONT: Configure APN

- AT+UBANDMASK: Set LTE/NB-IoT/GSM band masks.

## CH14 System Features

- AT+UTEMP: Internal temperature monitor

## CH29 MQTT

- AT+UMQTT: MQTT settings
    - 1: **Local Port**  
        Recommend to set local port to 0.  
        Other value might not work (But).

- AT+UMQTTNV: MQTT settings NVM

- AT+UMQTTC: MQTT operation  
    - 0: **Logout**   
        You have to logout to change MQTT settings.  
    - 1: **Login**  
        You need to login to send message.  

- AT+MQTTER: Show last failed MQTT error code

## CH30 MQTT-SN
This is a low-power MQTT protocol for device with constrained resources like battery, network etc.

## Module Configuration  

- AT&F: Set to factory defined configuration &F  