#include <stdio.h>
#include <termios.h>  /* Adding POSIX style terminal control*/
#include <unistd.h>   /* Standard UNIX definitions*/
#include <fcntl.h>    /* File control */
#include <errno.h>
#include <iostream>
#include <string.h>
#include <vector>
#include <thread>
#include <iostream> 
#include <fstream> 
#include <cstdlib> 
#include <bitset>


using namespace std;

/*  Initialize the serial port */
int serial_init(int port_no) {


    int serial_port = 0;
    char* device_name = new char[100];

    sprintf(device_name, "/dev/pts/%d", port_no);

    serial_port = open(device_name, O_RDWR);

    if (serial_port < 0) { 
        std::cout <<  "Error opening port :(( \nError No: " << errno << endl;
        return 0;
    } 
    else{
        std::cout << "Yay!  Opened port! \n";
    }
    int speed = B1152000;
    struct termios SerialPortSettings;
    tcgetattr(serial_port, &SerialPortSettings);
    cfsetispeed(&SerialPortSettings, 1152000);
    cfsetospeed(&SerialPortSettings, 1152000);
    SerialPortSettings.c_cflag &= ~PARENB;
    SerialPortSettings.c_cflag &= ~CSTOPB;
    SerialPortSettings.c_cflag &= ~CSIZE;
    SerialPortSettings.c_cflag |= CS8;
    SerialPortSettings.c_cflag &= ~CRTSCTS;
    SerialPortSettings.c_cflag |= CREAD | CLOCAL;
    SerialPortSettings.c_iflag &= ~(IXON |IXOFF|IXANY);
    SerialPortSettings.c_iflag &= ~(ICANON |ECHO | ECHOE | ISIG);
    SerialPortSettings.c_oflag &= ~OPOST;
    SerialPortSettings.c_cc[VMIN] = 1;
    SerialPortSettings.c_cc[VTIME] = 0;

    //  CHECK AGAINST THE DATASHEET AND RS232 SPEC

    if((tcsetattr(serial_port, TCSANOW, &SerialPortSettings)) != 0){
        printf("\n Error in setting Attributes!!!  Please check my code because something has gone terribly wrong :(( \n");
    }
    else {
        std:cout << "Baud rate is: " << cfgetispeed(&SerialPortSettings) << endl;
    } 

    return serial_port;
}

// simple func to send serial data easily
int send_serial(char* msg, int serial_port){
    int size = strlen(msg);
        write(serial_port, msg, size);
    return 0;
}

void start_ports(){
    system("socat -d -d pty,raw,echo=0 pty,raw,echo=0");
}

char dummy_byte(void){
    // Function to generate 3 bytes of dummy data (24bits)
    char byte = rand()%256;
    return byte;
}   

vector<int> find_ports(){
    char* device_name = new char[100];
    vector<int> valid_ports;

    for (int i=1;i<99;i++) 
        {
        // Prepare the port name (Linux)

        #ifdef __linux__
            sprintf(device_name, "/dev/pts/%d", i);
        #endif

        // try to connect to the device
        int port;
        port = open(device_name, O_RDWR);

        if (port >= 0)    
            {
                valid_ports.push_back(i);
                close(port);
            }
        }
    return valid_ports;
}

void serial_datagram(int serial_port){
    /*
    Datagram for serial no "0"
    */
    char identifier = 0xB7; // datagram Identifier for full datagram (20 bytes     )
    char term = 0b00001101;  // CR termination 
    
    int datagram_length = 20;
    char datagram[datagram_length];
    memset(datagram, 0, datagram_length); // set the datagram to all zeros
    datagram[0] = identifier;
    datagram[1] = 0b01001110;  
    datagram[20] = term;

    for (int i = 0; i < datagram_length; i++){
            cout << bitset<8>(datagram[i]) << endl;
            send_serial(&datagram[i], serial_port);
        }
}
/*  This function creates the "normal mode datagram as per the STIM300 datasheet section 5.5.6"*/
void normal_mode_datagram(int serial_port, bool startup = false, bool dummy_data = true){


    //int termination = 78;  //  This is byte 1 of the serial number datagram if there IS CR+TF termination
    char identifier = 0b10101111; // datagram Identifier for full datagram (64 bytes     )
    char STATUS = 0b00000000;

    /*  sorry this is a bit opaque but it sets the startup bit (bit 6) as per table 5-23*/
    if (startup) {
        STATUS = STATUS | 0b01000000; //  this uses the bitwise "OR" to set the startup bit to one
    }
    else{
        STATUS = STATUS & 0b10111111; // uses bitwise "AND" to set the startup bit to zero
    }


    int datagram_length = 64;
    char datagram[datagram_length];
    char CR = 0b00001101;
    memset(datagram, 0, datagram_length);

    datagram[0] = identifier;
    if (dummy_data){
    #pragma unroll
    for (int i = 1; i < 10; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 11; i < 20; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 21; i < 30; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 11; i < 37; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 38; i < 44; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 45; i < 51; i++){
        datagram[i] = dummy_byte();
    } 
    #pragma unroll
    for (int i = 51; i < 55; i++){
        datagram[i] = dummy_byte();
    } 
    }
    //cout << "Status Byte: " << bitset<8>(STATUS) << endl;
    datagram[10] = STATUS;
    datagram[20] = STATUS;
    datagram[30] = STATUS;
    datagram[37] = STATUS;
    datagram[44] = STATUS;
    datagram[51] = STATUS;
    datagram[55] = STATUS;
    datagram[63] = CR;
    //cout << datagram[0] << endl;

    for (int i = 0; i < datagram_length; i++){
        //cout << bitset<8>(datagram[i]) << endl;
        send_serial(&datagram[i], serial_port);
    }
}

void auto_normal_mode_datagram(int sleep_seconds, int serial_port, bool startup = false, bool dummy_data = true){
    normal_mode_datagram(serial_port, startup, dummy_data);
    sleep(sleep_seconds);
    auto_normal_mode_datagram(sleep_seconds, serial_port, dummy_data);
}

int poll_serial_in(int serial_port_in, int serial_port_out){
    string last_char = " ";


    char read_buff[128];
    memset(read_buff, 0, sizeof(read_buff));

    while(1){
        
    int n = read(serial_port_in, &read_buff, 1);

    if(n<0){
        cout<<"\nERROR!\n";
    }


    if (last_char == "N" & read_buff[0] == 0b00001101){
        cout << "Sending Normal Datagram" << endl;
        normal_mode_datagram(serial_port_out, false, true);

    }
    else if (last_char == "I" & read_buff[0] == 0b00001101){
        cout << "Sending Serial Datagram" << endl;
        serial_datagram(serial_port_out);

    }
    if(last_char != to_string(read_buff[0])){
        last_char = read_buff[0];
    }
    //poll_serial_in(serial_port_in);
    }
}


int main(void){
    // initialize the random number generator with time to give pseudorand ints
    srand(static_cast<unsigned int> (time(0)));
    

    std::thread t1(start_ports);
    sleep(1);
    int serial_port = serial_init(1);



    vector<int> ports = find_ports();
    cout << to_string(ports.size());
    for (int i = 0; i < ports.size(); i++){
        printf("Availiable ports: %d \n", ports[i]);
    }

    float frequency = 1;
    int port_num = 1;

    cout << "What serial port do you want to send data on?" << endl;
    cin >> port_num;
    
    int serial_port_out = serial_init(port_num);

    cout << "Please input the Frequency you want to send the normal mode datagram at: " << endl;    
    cin >> frequency;
    cout << "You have selected: " << frequency << "Hz" << endl;
    float temp = 1/frequency;
    
    int sleep_seconds = (int)temp;
    cout << "Sending datagram every " << sleep_seconds << " Seconds" << endl;
    
    
    // send serial number datagram on startup
    serial_datagram(serial_port_out);

    std::thread auto_thread(auto_normal_mode_datagram, sleep_seconds, serial_port_out, true, true);
    usleep(500);

    int pp;
    cout << "What serial port do you want to listen to?" << endl;
    cin >> pp;

    int serial_port_in = serial_init(pp);
    poll_serial_in(serial_port_in, serial_port_out);

    while(1){}
}