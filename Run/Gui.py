
from customtkinter import *
from tkinter import *
from tkinter import scrolledtext
import serial
import time
from datetime import datetime
from math import log, ceil

# from STIM300 data sheet pg38, table5-21
# x32 + x26 + x23 + x22 + x16 + x12 + x11 + x10 + x8 + x7 + x5 + x4 + x2 + x + 1

STIM300_divisor = 0b100000100110000010001110110110111

#def CRC_Check(data, divisor = STIM300_divisor):

class base_frame(CTkFrame):
    def __init(self, master):
        self.row = 0
        self.column = 0
        self.master = CTkFrame()

    def update_grid(self, row=2, column=0, rowspan=1,columnspan=1,sticky="nsew",padx=20,pady=10):
        self.row = row
        self.column = column
        self.grid(row = self.row, column = self.column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
    
    # class function to change the serial port
    def change_serial_port(self, new_port):
            self.serial_port.close()
            self.serial_port = self.root.serial_init(new_port)

    def listen_serial(self):
            bytes = 4
            listened = self.root.serial_listen.read(bytes)
            print(listened)

def CRC(dataword, generator):

    dword = dataword
    #find the length of the binary number in
    l_gen = generator.bit_length()
 
    # append 0s to dividend
    dividend = dword << (l_gen - 1)
 
    # shft specifies the no. of least significant
    # bits not being XORed
    shft = ceil(log(dividend + 1, 2)) - l_gen
 
    # ceil(log(dividend+1 , 2)) is the no. of binary
    # digits in dividend
 
    while dividend >= generator or shft >= 0:
 
        # bitwise XOR the MSBs of dividend with generator
        # replace the operated MSBs from the dividend with
        # remainder generated
        rem = (dividend >> shft) ^ generator
        dividend = (dividend & ((1 << shft) - 1)) | (rem << shft)
 
        # change shft variable
        shft = ceil(log(dividend+1, 2)) - l_gen
 
    # finally, AND the initial dividend with the remainder (=dividend)
    codeword = dword << (l_gen-1) | dividend
    print("Remainder:", bin(dividend))
    print("Codeword :", bin(codeword))

#CRC(0b10011101, 0b1001)


#################################
#  Dark mode is the best mode   #
#################################
set_appearance_mode("dark")#
#################################

class port_droplist(base_frame):
    def __init__(self, master):
        base_frame.__init__(self, master=master)

        #inherit the root app from master
        self.root = master.root
        #inherit the serial port from root
        self.serial_in = self.root.serial_in

        self.chosen_option_in = StringVar()
        self.chosen_option_out = StringVar()


        self.label_in = CTkLabel(self, text="input port").grid(row=0, column=0, padx=0, pady = [0, 5], sticky="nsew")
        self.checklist_in = CTkOptionMenu(master=self, values=self.get_ports(), command=lambda _: self.change_serial_in(new_port= int(self.chosen_option_in.get())), variable = self.chosen_option_in)
        self.checklist_in.grid(row=1, column=0, sticky="nsew", pady = [0, 5])


        self.label_out = CTkLabel(self, text="output port").grid(row=2, column=0, padx=0, pady = [0, 5], sticky="ew")
        self.checklist_out = CTkOptionMenu(master=self, values=self.get_ports(), command=lambda _: self.change_serial_out(new_port= int(self.chosen_option_out.get())), variable = self.chosen_option_out)
        self.checklist_out.grid(row=3, column=0, sticky="ew", pady = [0, 5])

    def change_serial_in(self, new_port):
        self.serial_in = self.root.change_serial_in(new_port = new_port)
    
    def change_serial_out(self, new_port):
        self.serial_out = self.root.change_serial_out(new_port = new_port)
    
    def get_ports(self):
        availiable_ports = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        availiable_ports = [str(element) for element in availiable_ports]

        #########################################################
        # properly impliment when you have time                 #
        #########################################################
        return availiable_ports
    


class send_frame(base_frame):
    def __init__(self, master):
        super(send_frame, self).__init__(master)
        
        # CTK Var to store user input
        self.text_in = ""
        self.root = master
        self.serial_out = self.root.serial_out


        #add buttons to trigger send event
        self.button = CTkButton(self, text = "Send Normal Mode Datagram", command = lambda: self.send_serial("N\r"))
        self.button.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        #add buttons to trigger send event
        self.button = CTkButton(self, text = "Send Serial Datagram", command = lambda: self.send_serial("I\r"))
        self.button.grid(row=1, column=0, sticky="ew", padx=20, pady=[0,10])
        
        #add label for buttons
        self.grid_columnconfigure(0, weight=1)
        self.label = CTkLabel(self, text="Press button to send custom command")
        self.label.grid(row=2, column=0, sticky="NS")

        #add entry for user input to be received.
        self.input = CTkEntry(self, textvariable=self.text_in, placeholder_text = "eg: 'N'")
        self.input.grid(row=3, column=0, padx=20, pady=10)
        #add buttons to trigger send event
        self.button = CTkButton(self, text = "Send Serial Datagram", command = self.send_entry)
        self.button.grid(row=4, column=0, sticky="ew", padx=20, pady=[0,10])

    def send_serial(self, char):
        self.serial_out.write(str.encode(char))

    def send_entry(self):
        #update variable and send via serial
        self.text_in = self.input.get()
        self.serial_out.write(str.encode(self.text_in))
        print(self.text_in)



class read_frame(base_frame):
    def __init__(self, master):
        super(read_frame, self).__init__(master)

        self.root = master
        self.serial_in = self.root.serial_in
        
        self.row = 2
        self.column = 0

        
        self.label = CTkLabel(self, text="Incoming serial data")
        self.label.grid(row=0, column=0, padx=2, pady=2,sticky="ew")

        self.serial_text = scrolledtext.ScrolledText(self, state="disabled")
        self.serial_text.grid(row=1,column=0,sticky="ew")
        

        self.update_grid(row=2, column=1)

        self.serial_scan()

    # class function to change the serial port
    def change_serial_port(self, new_port):
        self.serial_in.close()
        self.serial_in = self.root.change_serial_in(new_port)

    def serial_scan(self):
        self.serial_in = self.root.serial_in
        serial_in = self.serial_in.read(64)
        temp = int.from_bytes(serial_in, byteorder="big")
        if(temp != 0):
            self.update_text(bin(temp)+"\n")

        

        self.after(101, lambda: self.serial_scan())

    # update the text in the frame
    def update_text(self, text):
        self.serial_text.configure(state="normal")
        self.serial_text.insert(INSERT, text)
        self.serial_text.configure(state="disabled")
        
        ##Change from polling when have time##
        ## Might not be polling?  the pyserial library uses the system select func ??

class port_label(base_frame):
    def __init__(self, master):
        super(port_label, self).__init__(master)

        self.root = master.root
        self.serial = self.root.serial_in
        self.serial_out = self.root.serial_out
        self.text = "Currently sending data to port: " + self.serial.name

        self.column = 0
        self.row = 4

        self.label = CTkLabel(master=self, text = self.text)
        self.label.grid(row = 0, column = self.column, padx=5,pady=10, sticky="nsew")
        self.update_grid(row=4, column=0)

        self.update_text()


    # recursive function that updates itself every second to display the current serial port being used
    def update_text(self):
        self.serial = self.root.serial_in
        self.serial_out = self.root.serial_out

        temp_str = str(self.serial.name)[-1]
        self.text = "Currently receiving from port: " + temp_str + " \n " + "Currently sending to port: " + str(self.serial_out.name)[-1]
        self.label.configure(text=self.text)
        self.master.after(1000, self.update_text)


class MainFrame(base_frame):
    def __init__(self, master):
        super(MainFrame, self).__init__(master)

        self.root = master

        self.row = 0
        self.column = 0


        # add widgets onto the frame
        self.label = CTkLabel(master=self, text="  Please select the serial ports below: ")
        self.label.grid(row=0, column=0)

        self.checklist = port_droplist(self)
        self.checklist.update_grid(row=1, column=0)

        self.port_label = port_label(self)
        self.port_label.update_grid(row=6, column=0)
        
        #self.button = CTkButton(self, text = "listen", command = lambda: listen_serial(serial_listen, bytes = 4))
        #self.button.grid(row=1, column=0)


        self.columnspan = 3
        self.rowspan = 0

        self.update_grid(0, 0)


    def set_text(self, text):
        self.label.configure(text=text)


class App(CTk):
    def __init__(self):
        super().__init__()

        self.serial_in = self.serial_init(3)
        self.serial_out = self.serial_init(4)

        #Give the Gui a title
        self.title("STIM300 Serial Interface")
        #set windows dimensions
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


        #add in a frame
        self.my_frame = MainFrame(master=self)
        self.my_frame.update_grid(row = 0, column = 0)

        self.read_frame = read_frame(self)
        self.read_frame.update_grid(row = 0, column = 1, sticky="nsew")

        self.send_frame = send_frame(self)
        self.send_frame.update_grid(row=1, column=0, sticky="ns")


    def serial_init(self, port_number = 0, baud = 115200, timeout = 0):
        serial_port = serial.Serial('/dev/pts/'+ str(port_number), baudrate=baud, 
        timeout=timeout, parity = serial.PARITY_NONE, bytesize = serial.EIGHTBITS)
        serial_port.rtscts = False
        serial_port.dsrdtr = False

        return serial_port
    
    def change_serial_in(self, new_port, baud = 115200):
        if type(new_port) != int:
            print("please input an int")
            return 0
        if new_port < 0 | new_port > 99:
            print("invalid port number :(")
            return 0
            
        self.serial_in.close()
        temp = self.serial_init(port_number=new_port, baud=baud)
        if temp.isOpen():
            print("Now communitcating with port number: " + str(new_port) + "\n")
            self.serial_in = temp
            return self.serial_in

        else:
            print("Invalid Port")


    def change_serial_out(self, new_port, baud = 115200):

        if type(new_port) != int:
            print("please input an int")
            return 0
        if new_port < 0 | new_port > 99:
            print("invalid port number :(")
            return 0
            
        self.serial_out.close()
        temp = self.serial_init(port_number=new_port, baud=baud)

        if temp.isOpen():
            print("Now communitcating with port number: " + str(new_port) + "\n")
            self.serial_out = self.serial_init(port_number=new_port, baud=baud)
            temp.close()
            return self.serial_out

        else:
            print("Invalid Port")
            return self.serial_out


app = App()
app.mainloop()