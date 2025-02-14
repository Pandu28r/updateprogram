import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
from dynamixel_sdk import *
import pandas as pd
import csv
import numpy as np
import os
import  string
import keyboard as key

DEVICENAME = "COM6"
PROTOCOL_VERSION = 2.0
BAUDRATE = 1000000

ADDR_XL320_TORQUE = 24
ADDR_XL320_MOVING_SPEED = 32
ADDR_XL320_GOAL_POSITION = 30
COLOR = "#44b1de"

ADDR_XM430_TORQUE = 64
ADDR_XM430_VELOCITY = 112
ADDR_XM430_GOAL_POSITION = 116

XL320_ADDR_MOVING_SPEED             = 32
XM430_ADDR_PROFILE_ACCELERATION     = 108

XL320_ADDR_TORQUE_ENABLE            = 24
XL320_ADDR_GOAL_POSITION            = 30
XL320_ADDR_PRESENT_POSITION         = 37
XL320_ADDR_PROFILE_VELOCITY         = 32
XL320_LEN_GOAL_POSITION             = 2                     
XL320_LEN_PRESENT_POSITION          = 2 
XL320_LEN_COMBINED                  = 4

XM430_ADDR_TORQUE_ENABLE            = 64 
XM430_ADDR_GOAL_POSITION            = 116
XM430_ADDR_PRESENT_POSITION         = 132
XM430_ADDR_PROFILE_VELOCITY         = 112
XM430_LEN_GOAL_POSITION             = 4                      
XM430_LEN_PRESENT_POSITION          = 4
XM430_LEN_COMBINED                  = 8  

DXL_XL320 = [0,1,2,3,4,5,6,7,8,9,10,11,12]
DXL_XM430 = [13,14,15,16,17,18,19,20,21,22,23,24,25,26]
SERVOS = 0

def inisialisasi_port():
    global portHandler, packetHandler, groupSyncWrite_XL320, groupSyncWrite_XM430, groupSyncReadMove_XL320, groupSyncReadMove_XM430, groupSyncRead_XL320, groupSyncRead_XM430
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        quit()

    
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        quit()
    groupSyncWrite_XM430                = GroupSyncWrite(portHandler, packetHandler, 112, 8)
    groupSyncWrite_XL320                = GroupSyncWrite(portHandler, packetHandler, 30, 4)
    groupSyncReadMove_XL320             = GroupSyncRead(portHandler, packetHandler, 49,1)
    groupSyncReadMove_XM430             = GroupSyncRead(portHandler, packetHandler, 122,1)
    groupSyncRead_XL320                 = GroupSyncRead(portHandler, packetHandler, 37, 2)
    groupSyncRead_XM430                 = GroupSyncRead(portHandler, packetHandler, 132, 4)

    groupSyncWrite_XM430.clearParam()
    groupSyncWrite_XL320.clearParam()  
    groupSyncReadMove_XL320.clearParam() 
    groupSyncReadMove_XM430.clearParam()
    groupSyncRead_XL320.clearParam()
    groupSyncRead_XM430.clearParam()


    for DXL_ID in DXL_XM430:
        goal_pos = int(2047)
        goal_time = int(2000)
        Sync_Param=[DXL_LOBYTE(DXL_LOWORD(goal_time)), DXL_HIBYTE(DXL_LOWORD(goal_time)), DXL_LOBYTE(DXL_HIWORD(goal_time)), DXL_HIBYTE(DXL_HIWORD(goal_time)),DXL_LOBYTE(DXL_LOWORD(goal_pos)), DXL_HIBYTE(DXL_LOWORD(goal_pos)), DXL_LOBYTE(DXL_HIWORD(goal_pos)), DXL_HIBYTE(DXL_HIWORD(goal_pos))]
        dxl_addparam_result = groupSyncWrite_XM430.addParam(DXL_ID, Sync_Param)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncwrite_XM430 addparam failed" %DXL_ID)
        dxl_addparam_result = groupSyncRead_XM430.addParam(DXL_ID)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncRead_XM430 addparam failed" %DXL_ID)
        dxl_addparam_result = groupSyncReadMove_XM430.addParam(DXL_ID)
        if dxl_addparam_result != True:
           print("[ID:%03d] groupSyncMoveRead_XM430 addparam failed" %DXL_ID)
        
   
    for DXL_ID in DXL_XL320:
        goal_pos = int(511)
        goal_time = int(100)
        Sync_Param = [DXL_LOBYTE(DXL_LOWORD(goal_pos)), DXL_HIBYTE(DXL_LOWORD(goal_pos)), DXL_LOBYTE(DXL_LOWORD(goal_time)), DXL_HIBYTE(DXL_LOWORD(goal_time))]
        dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL_ID, Sync_Param)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupBulkWrite XL TIME addparam failed" % DXL_ID)
        dxl_addparam_result = groupSyncRead_XL320.addParam(DXL_ID)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncRead_XL320 addparam failed" % DXL_ID)
        dxl_addparam_result = groupSyncReadMove_XL320.addParam(DXL_ID)
        if dxl_addparam_result != True:
           print("[ID:%03d] groupSyncMoveRead_XL320 addparam failed" % DXL_ID)



class APP(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # app = ctk.CTk()
        self.title("Tim  AERORA")
        self.geometry("625x550")

        self.tabView = ctk.CTkTabview(self, width=600, height=525)
        self.tabView.pack(padx=20,pady=20)

        self.SERVO_KONDISI_TORQUE = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.SERVO_NYALA = []
        self.SERVO_MATI = []
        

        self.tabView.add("SERVO")
        self.tabView.add("LIHAT MOTION")
        self.tabView.add("REKAM MOTION")
        self.tabView.add("EDIT MOTION")
        self.tabView.add("CONVERT FILE CSV")


        self.tabKedua = ctk.CTkTabview(self.tabView.tab("CONVERT FILE CSV"), fg_color="#3D3C40")
        self.tabKedua.pack(padx=10,pady=10)

        self.tabKedua.add("Re-place")
        self.tabKedua.add("Buat Baru")

        self.tabKetiga = ctk.CTkTabview(self.tabView.tab("EDIT MOTION"), fg_color="#3D3C40")
        self.tabKetiga.pack(padx=10,pady=10)

        self.tabKetiga.add("Time")
        self.tabKetiga.add("Degree")

        self.tabKeempat = ctk.CTkTabview(self.tabView.tab("LIHAT MOTION"), fg_color="#3D3C40", height=275, width=330)
        self.tabKeempat.pack(padx=10,pady=10)

        self.tabKeempat.add("Per-Step")
        self.tabKeempat.add("Play Motion")

    # SWITCH VAR
        self.switch_var_semua = ctk.StringVar(value="off")
        self.switch_var_kepala = ctk.StringVar(value="off")
        self.switch_var_tangan_kanan = ctk.StringVar(value="off")
        self.switch_var_tangan_kiri = ctk.StringVar(value="off")
        self.switch_var_tangan = ctk.StringVar(value="off")
        self.switch_var_kaki_kanan = ctk.StringVar(value="off")
        self.switch_var_kaki_kiri = ctk.StringVar(value="off")
        self.switch_var_kaki = ctk.StringVar(value="off")
        self.switch_var_kondisi_perstep = ctk.StringVar(value="off")


    #  TAB ON SERVO
        self.switch_semua = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="SEMUA SERVO", command=self.all_servo,variable=self.switch_var_semua, onvalue="on", offvalue="off")
        self.switch_semua.pack(pady=20)
        self.switch_semua.place(relx=0.05,rely=0.17)
        self.switch_kepala = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="KEPALA", command=self.kepala,variable=self.switch_var_kepala, onvalue="on", offvalue="off")
        self.switch_kepala.pack(pady=20)
        self.switch_kepala.place(relx=0.05,rely=0.32)
        self.switch_semua_tangan = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="SEMUA TANGAN", command=self.tangan,variable=self.switch_var_tangan, onvalue="on", offvalue="off")
        self.switch_semua_tangan.pack(pady=20)
        self.switch_semua_tangan.place(relx=0.35,rely=0.1)
        self.switch_tangan_kanan = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="TANGAN KANAN", command=self.tangan_kanan,variable=self.switch_var_tangan_kanan, onvalue="on", offvalue="off")
        self.switch_tangan_kanan.pack(pady=20)
        self.switch_tangan_kanan.place(relx=0.35,rely=0.25)
        self.switch_tangan_kiri = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="TANGAN KIRI", command=self.tangan_kiri,variable=self.switch_var_tangan_kiri, onvalue="on", offvalue="off")
        self.switch_tangan_kiri.pack(pady=20)
        self.switch_tangan_kiri.place(relx=0.35,rely=0.4)
        self.switch_semua_kaki = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="SEMUA KAKI", command=self.kaki,variable=self.switch_var_kaki, onvalue="on", offvalue="off")
        self.switch_semua_kaki.pack(pady=20)
        self.switch_semua_kaki.place(relx=0.65,rely=0.1)
        self.switch_kaki_kanan = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="KAKI KANAN", command=self.kaki_kanan,variable=self.switch_var_kaki_kanan, onvalue="on", offvalue="off")
        self.switch_kaki_kanan.pack(pady=20)
        self.switch_kaki_kanan.place(relx=0.65,rely=0.25)
        self.switch_kaki_kiri = ctk.CTkSwitch(master=self.tabView.tab("SERVO"), text="KAKI KIRI", command=self.kaki_kiri,variable=self.switch_var_kaki_kiri, onvalue="on", offvalue="off")
        self.switch_kaki_kiri.pack(pady=20)
        self.switch_kaki_kiri.place(relx=0.65, rely=0.4)
        self.entry_id = ctk.CTkEntry(self.tabView.tab("SERVO"), placeholder_text="Masukkan ID Servo")
        self.entry_id.pack(pady=10)
        self.entry_id.place(relx=0.4,rely=0.6)
        self.button17 = ctk.CTkButton(self.tabView.tab("SERVO"), text="OFF SERVO id", command=self.off_servo_id, fg_color=COLOR)
        self.button17.place(relx=0.2,rely=0.77)
        self.button18 = ctk.CTkButton(self.tabView.tab("SERVO"), text="ON SERVO id", command=self.on_servo_id, fg_color=COLOR)
        self.button18.place(relx=0.6,rely=0.77)

        # TAB LIHAT MOTION
        self.switch_per_step = ctk.CTkSwitch(master=self.tabKeempat.tab("Per-Step"), text="OFF", command=self.kondisi_perstep,variable=self.switch_var_kondisi_perstep, onvalue="on", offvalue="off")
        self.switch_per_step.pack(pady=20)
        self.switch_per_step.place(relx=0.4,rely=0.07)
        self.label_perstep = ctk.CTkLabel(master=self.tabKeempat.tab("Per-Step"), text="Step  ", font=("Arial", 18))
        self.label_perstep.place(relx=0.35,rely=0.25)
        self.entry_name_lihat = ctk.CTkEntry(self.tabView.tab("LIHAT MOTION"), placeholder_text="Masukkan nama motion", width=170, height=30)
        self.entry_name_lihat.place(relx=0.35,rely=0.83)
        self.button_next = ctk.CTkButton(self.tabKeempat.tab("Per-Step"), text="<<", command=self.previous_step, fg_color=COLOR, width=100, font=("Arial", 20, "bold"))
        self.button_next.place(relx=0.1,rely=0.55)
        self.button_previous = ctk.CTkButton(self.tabKeempat.tab("Per-Step"), text=">>", command=self.next_step, fg_color=COLOR, width=100, font=("Arial", 20, "bold"))
        self.button_previous.place(relx=0.52,rely=0.55)
        self.button_play_motion_v4 = ctk.CTkButton(self.tabKeempat.tab("Play Motion"), text="PLAY MOTION V4", command=self.play_motion_v4, fg_color=COLOR)
        self.button_play_motion_v4.pack(pady=20)
        self.button_play_motion_v5 = ctk.CTkButton(self.tabKeempat.tab("Play Motion"), text="PLAY MOTION V5", command=self.anjay, fg_color=COLOR)
        self.button_play_motion_v5.pack(pady=20)
        self.button_play_motion_v6 = ctk.CTkButton(self.tabKeempat.tab("Play Motion"), text="PLAY MOTION V6", command=self.anjay, fg_color=COLOR)
        self.button_play_motion_v6.pack(pady=20)
        self.label = ctk.CTkLabel(self.tabView.tab("LIHAT MOTION"), text="Semangat Gaiss...")
        self.label.place(relx=0.41,rely=0.7)


        # TAB EDIT MOTION
        self.entry_name_edit = ctk.CTkEntry(self.tabView.tab("EDIT MOTION"), placeholder_text="Masukkan nama motion v6", width=170, height=30)
        self.entry_name_edit.pack(pady=15)
        self.entry_step = ctk.CTkEntry(self.tabView.tab("EDIT MOTION"), placeholder_text="Masukkan nomor step", height=30)
        self.entry_step.pack(pady=15)
        self.entry_servo_id = ctk.CTkEntry(self.tabKetiga.tab("Time"), placeholder_text="Masukkan servo ID")
        self.entry_servo_id.pack(pady=15)
        self.entry_time = ctk.CTkEntry(self.tabKetiga.tab("Time"), placeholder_text="Masukkan waktu")
        self.entry_time.pack(pady=15)
        self.button_save_time = ctk.CTkButton(self.tabKetiga.tab("Time"), text="SIMPAN", command=self.anjay)
        self.button_save_time.place(relx=0.25,rely=0.68)
        self.button_record_degree = ctk.CTkButton(self.tabKetiga.tab("Degree"), text="REKAM", command=self.anjay)
        self.button_record_degree.place(relx=0.25,rely=0.26)
        self.button_save_degree = ctk.CTkButton(self.tabKetiga.tab("Degree"), text="SIMPAN", command=self.anjay)
        self.button_save_degree.place(relx=0.25,rely=0.52)

        self.index = 0
        self.motion_data = []
        self.time_data = []
        self.type = ''
    # button19 = ctk.CTkButton(tabView.tab("EDIT MOTION"), text="PILIH WARNA", command=pilih_warna, fg_color=COLOR)
    # button19.place(relx=0.6,rely=0.93)
    def anjay(self):
        print('anjay')
    # # Fungsi untuk memilih warna
    # def pilih_warna():
    #     global COLOR
    #     root = tk.Tk()
    #     root.withdraw()  # Sembunyikan jendela utama
    #     warna = colorchooser.askcolor(title="Pilih Warna")
    #     COLOR = warna[1]

    def getIdByKondisiTorque(self):
        self.SERVO_MATI = []
        self.SERVO_NYALA = []
        for id,kondisi in enumerate(self.SERVO_KONDISI_TORQUE):
            if kondisi == 1:
                self.SERVO_NYALA.append(id)
            else:
                self.SERVO_MATI.append(id)
    
    def enable_torque(self, id_awal, id_akhir, type):
        list1 = list(range(id_awal,(id_akhir+1), type))
        id_list = list(set(list1) & set(self.SERVO_MATI))
        if not id_list:
            return
        for id in id_list:
            if id <= 12:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XL320_TORQUE, 1)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    self.SERVO_KONDISI_TORQUE[id] += 1
                    print("Servo#%d on" % id)
            else:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XM430_TORQUE, 1)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    self.SERVO_KONDISI_TORQUE[id] += 1
                    print("Servo#%d on" % id)

    def disable_torque(self, id_awal, id_akhir, type):
        list1 = list(range(id_awal,(id_akhir+1), type))
        id_list = list(set(list1) & set(self.SERVO_NYALA))
        if not id_list:
            return
        for id in id_list:
            if id <= 12:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XL320_TORQUE, 0)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    self.SERVO_KONDISI_TORQUE[id] -= 1
                    print("Servo#%d of" % id)
            else:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XM430_TORQUE, 0)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    self.SERVO_KONDISI_TORQUE[id] -= 1
                    print("Servo#%d of" % id)

    def kepala(self):
        if self.switch_kepala.get() == 'on':
            self.on_servo(1)
        else:
            self.off_servo(1)
        self.kondisi_all_servo()

    def tangan(self):
        if self.switch_semua_tangan.get() == 'on':
            self.switch_var_tangan_kanan.set('on')
            self.switch_var_tangan_kiri.set('on')
            self.on_servo(2)
        else:
            self.switch_var_tangan_kanan.set('off')
            self.switch_var_tangan_kiri.set('off')
            self.off_servo(2)
        self.kondisi_all_servo()

    def tangan_kanan(self):
        if self.switch_var_tangan_kanan.get() == 'on':
            self.on_servo(4)
        else:
            self.off_servo(4)
        self.kondisi_servo_tangan()
        self.kondisi_all_servo()

    def tangan_kiri(self):
        if self.switch_var_tangan_kiri.get() == 'on':
            self.on_servo(5)
        else:
            self.off_servo(5)
        self.kondisi_servo_tangan()
        self.kondisi_all_servo()

    def kaki(self):
        if self.switch_var_kaki.get() == 'on':
            self.switch_var_kaki_kanan.set('on')
            self.switch_var_kaki_kiri.set('on')
            self.on_servo(3)
        else:
            self.switch_var_kaki_kiri.set('off')
            self.switch_var_kaki_kanan.set('off')
            self.off_servo(3)
        self.kondisi_all_servo()
    
    def kaki_kanan(self):
        if self.switch_var_kaki_kanan.get() == 'on':
            self.on_servo(6)
        else:
            self.off_servo(6)
        self.kondisi_servo_kaki()
        self.kondisi_all_servo()
    
    def kaki_kiri(self):
        if self.switch_var_kaki_kiri.get() == 'on':
            self.on_servo(7)
        else:
            self.off_servo(7)
        self.kondisi_servo_kaki()
        self.kondisi_all_servo()

    def kondisi_kepala(self):
        list = self.SERVO_KONDISI_TORQUE[0:3]
        if all(list) is True:
            self.switch_var_kepala.set('on')
        else:
            self.switch_var_kepala.set('off')

    def kondisi_tangan(self):
        if all(self.SERVO_KONDISI_TORQUE[3:15:2]) is True:
            self.switch_var_tangan_kanan.set('on')
        else:
            self.switch_var_tangan_kanan.set('off')
        if all(self.SERVO_KONDISI_TORQUE[4:15:2]) is True:
            self.switch_var_tangan_kiri.set('on')
        else:
            self.switch_var_tangan_kiri.set('off')

    def kondisi_kaki(self):
        if all(self.SERVO_KONDISI_TORQUE[15:27:2]) is True:
            self.switch_var_kaki_kanan.set('on')
        else:
            self.switch_var_kaki_kanan.set('off')
        if all(self.SERVO_KONDISI_TORQUE[16:27:2]) is True:
            self.switch_var_kaki_kiri.set('on')
        else:
            self.switch_var_kaki_kiri.set('off')

    def kondisi_all_servo(self):
        if self.switch_var_kepala.get() == 'on':
            kondisi_kepala = 1
        else:
            kondisi_kepala = 0
        if self.switch_var_kaki.get() == 'on':
            kondisi_kaki = 1
        else:
            kondisi_kaki = 0
        if self.switch_var_tangan.get() == 'on':
            kondisi_tangan = 1
        else:
            kondisi_tangan = 0
        temp = [kondisi_tangan, kondisi_kaki, kondisi_kepala]
        if all(temp) is True:
            self.switch_var_semua.set('on')
        else:
            self.switch_var_semua.set('off')
        print(self.SERVO_KONDISI_TORQUE)
    
    def kondisi_servo_tangan(self):
        if self.switch_var_tangan_kanan.get() == 'on':
            kondisi_tangan_kanan = 1
        else:
            kondisi_tangan_kanan = 0
        if self.switch_var_tangan_kiri.get() == 'on':
            kondisi_tangan_kiri = 1
        else:
            kondisi_tangan_kiri = 0
        temp = [kondisi_tangan_kanan, kondisi_tangan_kiri]
        if all(temp) is True:
            self.switch_var_tangan.set('on')
        else:
            self.switch_var_tangan.set('off')
    
    def kondisi_servo_kaki(self):
        if self.switch_var_kaki_kanan.get() == 'on':
            kondisi_kaki_kanan = 1
        else:
            kondisi_kaki_kanan = 0
        if self.switch_var_kaki_kiri.get() == 'on':
            kondisi_kaki_kiri = 1
        else:
            kondisi_kaki_kiri = 0
        temp = [kondisi_kaki_kanan, kondisi_kaki_kiri]
        if all(temp) is True:
            self.switch_var_kaki.set('on')
        else:
            self.switch_var_kaki.set('off')

    def all_servo(self):
        id_awal = 0
        id_akhir = 26
        if self.switch_var_semua.get() == 'on':
            self.switch_var_kepala.set('on')
            self.switch_var_tangan.set('on')
            self.switch_var_kaki.set('on')
            self.switch_var_tangan_kanan.set('on')
            self.switch_var_tangan_kiri.set('on')
            self.switch_var_kaki_kanan.set('on')
            self.switch_var_kaki_kiri.set('on')

            self.on_servo(8)
        else:
            self.switch_var_kepala.set('off')
            self.switch_var_tangan.set('off')
            self.switch_var_kaki.set('off')
            self.switch_var_tangan_kanan.set('off')
            self.switch_var_tangan_kiri.set('off')
            self.switch_var_kaki_kanan.set('off')
            self.switch_var_kaki_kiri.set('off')

            self.off_servo(8)
        self.kondisi_all_servo()

    def off_servo(self, type):
        self.getIdByKondisiTorque()
        if type == 1:
            self.disable_torque(0,2,1)
        elif type == 2:
            self.disable_torque(3,14,1)
        elif type == 3:
            self.disable_torque(15,26,1)
        elif type == 4:
            self.disable_torque(3,14,2)
        elif type == 5:
            self.disable_torque(4,14,2)
        elif type == 6:
            self.disable_torque(15,26,2)
        elif type == 7:
            self.disable_torque(16,26,2)
        elif type == 8:
            self.disable_torque(0,26,1)
        else:
            print("Salah memasukan type")

    def on_servo(self, type):
        self.getIdByKondisiTorque()
        if type == 1:
            self.enable_torque(0,2,1)
        elif type == 2:
            self.enable_torque(3,14,1)
        elif type == 3:
            self.enable_torque(15,26,1)
        elif type == 4:
            self.enable_torque(3,14,2)
        elif type == 5:
            self.enable_torque(4,14,2)
        elif type == 6:
            self.enable_torque(15,26,2)
        elif type == 7:
            self.enable_torque(16,26,2)
        elif type == 8:
            self.enable_torque(0,26,1)
        else:
            print("Salah memasukan type")

    def off_servo_id(self):
        id_string = self.entry_id.get()
        id1 = id_string.split(',')
        id_int_list = list(map(int, id1))
        self.getIdByKondisiTorque()
        id_list = list(set(id_int_list) & set(self.SERVO_NYALA))
        print(id_list)
        if not id_list:
            return
        for id in id_list:
            if id <= 12:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XL320_TORQUE, 0)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    print("Servo#%d of" % id)
                    self.SERVO_KONDISI_TORQUE[id] -= 1
            else:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XM430_TORQUE, 0)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    print("Servo#%d of" % id)
                    self.SERVO_KONDISI_TORQUE[id] -= 1
        self.kondisi_kepala()
        self.kondisi_tangan()
        self.kondisi_kaki()
        self.kondisi_servo_tangan()
        self.kondisi_servo_kaki()
        self.kondisi_all_servo()

    def on_servo_id(self):
        id_string = self.entry_id.get()
        id1 = id_string.split(',')
        id_int_list = list(map(int, id1))
        self.getIdByKondisiTorque()
        id_list = list(set(id_int_list) & set(self.SERVO_MATI))
        print(id_list)
        if not id_list:
            return
        for id in id_list:
            print(id)
            if id <= 12:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XL320_TORQUE, 1)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    print("Servo#%d of" % id)
                    self.SERVO_KONDISI_TORQUE[id] += 1
            else:
                dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_XM430_TORQUE, 1)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % packetHandler.getRxPacketError(dxl_error))
                else:
                    print("Servo#%d of" % id)
                    self.SERVO_KONDISI_TORQUE[id] += 1
        self.kondisi_kepala()
        self.kondisi_tangan()
        self.kondisi_kaki()
        self.kondisi_servo_tangan()
        self.kondisi_servo_kaki()
        self.kondisi_all_servo()


    ##############################################
    ##########       LIHAT MOTION       ##########
    ##############################################

    #########       PER-STEP        #########
    def konversi(self, input, Ibawah, Iatas, Obawah, Oatas):
        return (input - Ibawah) / (Iatas - Ibawah) * (Oatas - Obawah)


    def view_motion_baru(self):
        name = self.entry_name_lihat.get()
        path = f'motion_baru/{name}.csv'
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                dxl_columns = [f'DXL#{i}' for i in range(27)]
                cek_columns_v6 =  [f'T_XL320#{i}' for i in range(13)] + [f'T_XM430#{i}' for i in range(13,27)] + [f'DXL#{i}' for i in range(27)]
                time_columns_v6 = [f'T_XL320#{i}' for i in range(13)] + [f'T_XM430#{i}' for i in range(13,27)]
                cek_columns =  ['T_XL320', 'T_XM430'] + [f'DXL#{i}' for i in range(27)]
                time_columns =  ['T_XL320', 'T_XM430']
                if all(col in df.columns for col in cek_columns_v6):
                    self.motion_data = df[dxl_columns].values.tolist()
                    self.time_data = df[time_columns_v6].values.tolist()
                    self.type = 'v6'
                    self.getIdByKondisiTorque()
                    self.enable_torque(0,27,1)
                    self.kondisi_kepala()
                    self.kondisi_tangan()
                    self.kondisi_kaki()
                    self.kondisi_servo_tangan()
                    self.kondisi_servo_kaki()
                    self.kondisi_all_servo()
                    self.play_motion_gui()
                elif all(col in df.columns for col in cek_columns):
                    self.motion_data = df[dxl_columns].values.tolist()
                    self.time_data = df[time_columns].values.tolist()
                    self.type = 'anjay'
                    self.getIdByKondisiTorque()
                    self.enable_torque(0,27,1)
                    self.kondisi_kepala()
                    self.kondisi_tangan()
                    self.kondisi_kaki()
                    self.kondisi_servo_tangan()
                    self.kondisi_servo_kaki()
                    self.kondisi_all_servo()
                    self.play_motion_gui()
                else:
                    print("Kolom pada file salah.")
            except Exception as e:
                print(f"Terjadi kesalahan saat memuat file: {e}")
        else:
            print("File motion tidak ditemukan. Pastikan nama file sesuai dan berada di folder 'motion_baru'.")

    def play_motion_gui(self):
        step_data = self.motion_data[self.index]
        step_time = self.time_data[self.index]
        print(step_data)
        print(step_time)
        print(self.type)
        print(f"Step {self.index+1}/{len(self.motion_data)}")
        if self.type == 'v6': 
            for DXL1_ID, position in enumerate(step_data):
                if DXL1_ID < 13:
                    position_value = int(self.konversi(int(position), 0, 300, 0, 1023))
                    time_value = step_time[DXL1_ID]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)), DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value))]
                    dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
                else:
                    position_value = int(self.konversi(int(position), 0, 360, 0, 4095))
                    time_value = step_time[DXL1_ID]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value)),
                                DXL_LOBYTE(DXL_HIWORD(time_value)), DXL_HIBYTE(DXL_HIWORD(time_value)),
                                DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)),
                                DXL_LOBYTE(DXL_HIWORD(position_value)), DXL_HIBYTE(DXL_HIWORD(position_value))]
                    dxl_addparam_result = groupSyncWrite_XM430.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
        else:
            for DXL1_ID, position in enumerate(step_data):
                if DXL1_ID < 13:
                    position_value = int(self.konversi(int(position), 0, 300, 0, 1023))
                    time_value = step_time[0]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)), DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value))]
                    dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
                else:
                    position_value = int(self.konversi(int(position), 0, 360, 0, 4095))
                    time_value = step_time[1]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value)),
                                DXL_LOBYTE(DXL_HIWORD(time_value)), DXL_HIBYTE(DXL_HIWORD(time_value)),
                                DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)),
                                DXL_LOBYTE(DXL_HIWORD(position_value)), DXL_HIBYTE(DXL_HIWORD(position_value))]
                    dxl_addparam_result = groupSyncWrite_XM430.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
        dxl_comm_result = groupSyncWrite_XL320.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        dxl_comm_result = groupSyncWrite_XM430.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        groupSyncWrite_XM430.clearParam()
        groupSyncWrite_XL320.clearParam()
        self.label_perstep.configure(text=f"Step {self.index+1}/{len(self.motion_data)}")

    def next_step(self):
        if self.switch_var_kondisi_perstep.get() == 'on':
            if self.index < len(self.motion_data) - 1:
                self.index += 1
                self.play_motion_gui()
    
    def previous_step(self):
        if self.switch_var_kondisi_perstep.get() == 'on':
            if self.index > 0:
                self.index -= 1
                self.play_motion_gui()

    def kondisi_perstep(self):
        if self.switch_var_kondisi_perstep.get() == 'on':
            self.switch_per_step.configure(text="ON")
            self.index = 0
            self.view_motion_baru()
        else:
            self.switch_per_step.configure(text="OFF")
            self.motion_data = []
            self.time_data = []
            self.label_perstep.configure(text=f"Step  ")

    #########       PLAY MOTION        #########
    def play_motion_v4(self):
        nama_file = self.entry_name_lihat.get()
        print(nama_file)
        self.gerak_by_motion_v4(nama_file)
        print("Selesai")



    def bacaFile(self, FILE_NAME):
        global MOTION_TIME_XM430,MOTION_TIME_XL320,MOTION_DXL_XL320,MOTION_DXL_XM430,MOTION_DXL
        file = open(FILE_NAME)
        csvreader = csv.reader(file)
        header = next(csvreader)
        
        MOTION_TIME_XM430 = [] #menyimpan bagian time
        MOTION_TIME_XL320 = [] #menyimpan bagian time
        MOTION_DXL_XL320 = [] #menyimpan posisi dxl 0-14
        MOTION_DXL_XM430 = [] #menyimpan posisi dxl 15-
        MOTION_DXL=[]
        for row in csvreader:
            MOTION_TIME_XM430.append(row[2])
            MOTION_TIME_XL320.append(row[1])
            MOTION_DXL.append(row[3:])
            MOTION_DXL_XL320.append(row[3:18])
            MOTION_DXL_XM430.append(row[18:30])
        
        file.close()
        return MOTION_DXL
    
    def getIndexByNotElement(self,array,element):
        j = 0
        index = []
        for i in array:
            if(i != element):
                index.append(j)
            j+=1
        return index
    
    def getNotValue(self, array,element):
        index = []
        for i in array:
            if(i != element):
                index.append(int(i))
        return index
    
    def getNotValue_v2(self, array,element):
        global DXL_KAKI_KIRI, DXL_KAKI_KANAN
        DXL_KAKI_KIRI = [16,18,20,22,24,26]
        DXL_KAKI_KANAN = [15,17,19,21,23,25]
        j=0
        index_xl320 = []
        index_xm430 = []
        for i in array:
            if(i != element):
                if j in DXL_KAKI_KIRI or j in DXL_KAKI_KANAN or j == 13 or j == 14:
                    index_xm430.append(int(i))
                else:
                    index_xl320.append(int(i))
            j+=1
        return index_xl320, index_xm430

    def gerak_by_motion_v4(self, NAMA_FILE, THRESHOLD_XL320=10, THRESHOLD_XM430=5,awal=1):
        global DXL_XM430
        DXL_XM430 = [13,14,15,16,17,18,19,20,21,22,23,24,25,26]
        print(NAMA_FILE)
        #bacaFile(FILE2)
        self.bacaFile(NAMA_FILE)
        groupSyncWrite_XM430.clearParam()
        for i in range(len(MOTION_DXL)):
            finish=0
        
            i = int(i)
            DXL_IDS = self.getIndexByNotElement(MOTION_DXL[i],"-1")
            DXL_DEGREE = self.getNotValue(MOTION_DXL[i],"-1")
            DXL_DEGREE_XL320, DXL_DEGREE_XM430 = self.getNotValue_v2(MOTION_DXL[i],"-1")
            print( "MOTION : ",NAMA_FILE," STEP : ",i)
            timeout=0
            print(DXL_DEGREE)
            print(DXL_IDS)
            print(MOTION_TIME_XM430)
            
            for ids,DXL_ID in enumerate(DXL_IDS):
                if DXL_ID in DXL_XM430:
                    goal_pos = int(self.konversi(DXL_DEGREE[ids],0,360,0,4095))
                    goal_time = int(MOTION_TIME_XM430[i])
                    Sync_Param=[DXL_LOBYTE(DXL_LOWORD(goal_time)), DXL_HIBYTE(DXL_LOWORD(goal_time)), DXL_LOBYTE(DXL_HIWORD(goal_time)), DXL_HIBYTE(DXL_HIWORD(goal_time)),DXL_LOBYTE(DXL_LOWORD(goal_pos)), DXL_HIBYTE(DXL_LOWORD(goal_pos)), DXL_LOBYTE(DXL_HIWORD(goal_pos)), DXL_HIBYTE(DXL_HIWORD(goal_pos))]
                    dxl_addparam_result = groupSyncWrite_XM430.addParam(DXL_ID, Sync_Param)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite XM TIME addparam failed" % DXL_ID)
                else:
                    goal_pos = int(self.konversi(DXL_DEGREE[ids],0,300,0,1023))
                    goal_time = int(MOTION_TIME_XL320[i])
                    Sync_Param = [DXL_LOBYTE(DXL_LOWORD(goal_pos)), DXL_HIBYTE(DXL_LOWORD(goal_pos)), DXL_LOBYTE(DXL_LOWORD(goal_time)), DXL_HIBYTE(DXL_LOWORD(goal_time))]
                    dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL_ID, Sync_Param)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite XL TIME addparam failed" % DXL_ID)
            
            dxl_comm_result=groupSyncWrite_XL320.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s anjay" % packetHandler.getTxRxResult(dxl_comm_result))
            dxl_comm_result=groupSyncWrite_XM430.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                print("1")
        
            groupSyncWrite_XL320.clearParam()
            groupSyncWrite_XM430.clearParam()
            while True:
                if key.is_pressed(' '):
                    print("selesai")
                    break
                
                    
                    
                # Read present position
                dxl_present_position_xm430 = []
                dxl_present_position_xl320 = []
                dxl_present_condition_xm430 = []
                dxl_present_condition_xl320 = []

                
                dxl_comm_result = groupSyncReadMove_XL320.txRxPacket()
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result),"xlmove")
                dxl_comm_result = groupSyncReadMove_XM430.txRxPacket()
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result),"xmmove")
                dxl_comm_result = groupSyncRead_XM430.txRxPacket()
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result),"xmpos")
                dxl_comm_result = groupSyncRead_XL320.txRxPacket()
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % packetHandler.getTxRxResult(dxl_comm_result),"xlpos")
            
                for DXL_ID in DXL_IDS:
                    if DXL_ID in DXL_XM430:
                        dxl_getdata_result = groupSyncRead_XM430.isAvailable(DXL_ID, XM430_ADDR_PRESENT_POSITION, XM430_LEN_PRESENT_POSITION)
                        #if dxl_getdata_result != True:
                        #  print("[ID:%03d] groupBulkRead getdata failed" % DXL_ID)
                        sudut = groupSyncRead_XM430.getData(DXL_ID, XM430_ADDR_PRESENT_POSITION, XM430_LEN_PRESENT_POSITION)
                        dxl_present_position_xm430.append (self.konversi(sudut,0,4095,0,360))

                        dxl_getdata_result = groupSyncReadMove_XM430.isAvailable(DXL_ID, 122, 1)
                        #if dxl_getdata_result != True:
                        #  print("[ID:%03d] groupBulkReadMove getdata failed" % DXL_ID)
                        dxl_present_condition_xm430.append(groupSyncReadMove_XM430.getData(DXL_ID, 122, 1))
                    else:
                        dxl_getdata_result = groupSyncRead_XL320.isAvailable(DXL_ID, XL320_ADDR_PRESENT_POSITION, XL320_LEN_PRESENT_POSITION)
                        #if dxl_getdata_result != True:
                        #  print("[ID:%03d] groupBulkRead getdata failed" % DXL_ID)
                        sudut = groupSyncRead_XL320.getData(DXL_ID, XL320_ADDR_PRESENT_POSITION, XL320_LEN_PRESENT_POSITION)
                        dxl_present_position_xl320.append (self.konversi(sudut,0,1023,0,300))

                        dxl_getdata_result = groupSyncReadMove_XL320.isAvailable(DXL_ID, 49, 1)
                        #if dxl_getdata_result != True:
                        # print("[ID:%03d] groupBulkReadMove getdata failed" % DXL_ID)
                        dxl_present_condition_xl320.append(groupSyncReadMove_XL320.getData(DXL_ID, 49, 1))
                dxl_present_position_xl320 = np.asarray(dxl_present_position_xl320)
                dxl_present_position_xm430 = np.asarray(dxl_present_position_xm430)
                DXL_DEGREE_XL320 = np.asarray(DXL_DEGREE_XL320)
                DXL_DEGREE_XM430 = np.asarray(DXL_DEGREE_XM430)
                hasil_XL320 = dxl_present_position_xl320-DXL_DEGREE_XL320
                hasil_XM430 = dxl_present_position_xm430-DXL_DEGREE_XM430
                
                combined_condition=dxl_present_condition_xl320+dxl_present_condition_xm430
                while all(j == 0 for j in combined_condition) is True:
                    timeout+=1
                    print("timeout",timeout)
                    time.sleep(0.04)
                    break
                
                if all(abs(i) <= THRESHOLD_XL320 for i in hasil_XL320) is True and all(abs(i) <= THRESHOLD_XM430 for i in hasil_XM430) is True or timeout>1:
                    break
                
                ###CHECK SERVO YANG BELUM SELESAI
            #   for i,nilai in enumerate(hasil_XL320):
            #      if abs(nilai)>=THRESHOLD_XL320:
            #         print("ID :",i-0)
                #for i,nilai in enumerate(hasil_XM430):
                #   if abs(nilai)>=THRESHOLD_XM430:
                #      print("ID :",i+13)
                #pub.publish(urutan_gerak)
                # rospy.sleep(0.01)



if __name__ == "__main__":
    inisialisasi_port()
    app = APP() 
    app.mainloop()