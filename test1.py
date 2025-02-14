import customtkinter as ctk
import tkinter as tk

# Initialize the main window
root = ctk.CTk()
root.geometry("300x200")
root.title("CustomTkinter Switch Button Example")



# Function to handle switch state change
def kepala():
    print("anjay")
    if switch_var1.get() == 'on':
        b = 1
    else:
        b = 0
    if switch_var.get() == 'on':
        c = 1
    else:
        c=0

    a = [b, c]
    if all(a) is True:
        switch_var2.set('on')
        print("aaa")
    else:
        switch_var2.set('off')

def switch_event():
    global switch_var
    if switch_var.get() == "on":
        label.configure(text="Switch is ON")
        print(switch_var.get() + " 1")
        kepala()
    else:
        label.configure(text="Switch is OFF")
        print(switch_var.get() + " 1")
        kepala()


def switch_event1():
    global switch_var1
    if switch_var1.get() == "on":
        label.configure(text="Switch is ON")
        print(switch_var1.get() + " 2")
        kepala()
    else:    
        label.configure(text="Switch is OFF")
        print(switch_var1.get() + " 2")
        kepala()

def switch_event2():
    global switch_var2
    if switch_var2.get() == "on":
        label.configure(text="Switch is ON")
        switch_var.set('on')
        switch_var1.set('on')
        print(switch_var2.get() + " 3")
    else:
        label.configure(text="Switch is OFF")
        print(switch_var.get())
        switch_var.set('off')
        switch_var1.set('off')
        print(switch_var2.get() + " 3")

switch_var = ctk.StringVar(value="off")
switch_var1 = ctk.StringVar(value="off")
switch_var2 = ctk.StringVar(value="off")

switch = ctk.CTkSwitch(master=root, text="CTkSwitch", command=switch_event,variable=switch_var, onvalue="on", offvalue="off")
switch.pack(pady=20)
switch2 = ctk.CTkSwitch(master=root, text="CTkSwitch", command=switch_event1,variable=switch_var1, onvalue="on", offvalue="off")
switch2.pack(pady=20)
switch2 = ctk.CTkSwitch(master=root, text="CTkSwitch", command=switch_event2,variable=switch_var2, onvalue="on", offvalue="off")
switch2.pack(pady=20)

# Create a switch button
# switch = ctk.CTkSwitch(master=root, text="Toggle Switch", command=switch_event)
# switch.pack(pady=20)

# Create a label to display switch state
label = ctk.CTkLabel(master=root, text="Switch is OFF")
label.pack(pady=20)

# Run the application
root.mainloop()
