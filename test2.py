import customtkinter as ctk

# List bertipe string
SERVO_KONDISI_TORQUE = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
SERVO_MATI = []
SERVO_NYALA = []
# Menggunakan map() untuk mengubah elemen menjadi integer


# Menampilkan hasil
def getIdByKondisiTorque():
    global SERVO_NYALA, SERVO_MATI
    SERVO_MATI = []
    SERVO_NYALA = []
    for id,kondisi in enumerate(SERVO_KONDISI_TORQUE):
        if kondisi == 1:
            SERVO_NYALA.append(id)
        else:
            SERVO_MATI.append(id)

def kepala():
    getIdByKondisiTorque()
    
getIdByKondisiTorque()
print(SERVO_NYALA)
print(SERVO_MATI)

# Initialize the main window
root = ctk.CTk()
root.geometry("300x350")
root.title("CustomTkinter Switch Button Example")



# Function to handle switch state change
def kondisiSemuaServo():
    if switch_var1.get() == 'on':
        b = 1
    else:
        b = 0
    if switch_var.get() == 'on':
        c = 1
    else:
        c=0
    if switch_var2.get() == 'on':
        d = 1
    else:
        d = 0

    a = [b, c, d]
    if all(a) is True:
        switch_var3.set('on')
    else:
        switch_var3.set('off')

def switch_event():
    kondisiSemuaServo()

def switch_event1():
    kondisiSemuaServo()

def switch_event2():
    kondisiSemuaServo()

def switch_event3():
    if switch_var3.get() == 'on':
        switch_var.set('on')
        switch_var1.set('on')
        switch_var2.set('on')
    else:
        switch_var.set('off')
        switch_var1.set('off')
        switch_var2.set('off')


    

switch_var = ctk.StringVar(value="off")
switch_var1 = ctk.StringVar(value="off")
switch_var2 = ctk.StringVar(value="off")
switch_var3 = ctk.StringVar(value="off")

switch = ctk.CTkSwitch(master=root, text="Kepala", command=switch_event,variable=switch_var, onvalue="on", offvalue="off")
switch.pack(pady=20)
switch2 = ctk.CTkSwitch(master=root, text="Tangan", command=switch_event1,variable=switch_var1, onvalue="on", offvalue="off")
switch2.pack(pady=20)
switch2 = ctk.CTkSwitch(master=root, text="Kaki", command=switch_event2,variable=switch_var2, onvalue="on", offvalue="off")
switch2.pack(pady=20)
switch3 = ctk.CTkSwitch(master=root, text="Semua", command=switch_event3,variable=switch_var3, onvalue="on", offvalue="off")
switch3.pack(pady=20)

# Create a switch button
# switch = ctk.CTkSwitch(master=root, text="Toggle Switch", command=switch_event)
# switch.pack(pady=20)

# Create a label to display switch state
label = ctk.CTkLabel(master=root, text="Switch is OFF")
label.pack(pady=20)

# Run the application
root.mainloop()
