# STIM300_data_stub
Data stub for the STIM300 gyro/accellerometer with gui to access data in/out


# Run Instructions
To run the code, please run the following commands

### Run using Bash
Navigate to "Run" dir

Run the following command `bash automate.sh` when in the "Run" dir


### Manual
To install the virtual port tool please use this command:

`sudo apt-get install socat -y
`

Then run the c++ data stub

`./datastub`

Then start up the Gui

`python3 Gui.py`
