import os
import time
import pandas as pd
import customtkinter as ctk
from dynamixel_sdk import *
import csv
import numpy as np

XL320_TORQUE_ENABLE = 24
XM430_ADDR_TORQUE_ENABLE = 64
XL320_PRESENT_POSITION = 37
XM430_PRESENT_POSITION = 132
XL320_GOAL_POSITION = 30
XM430_GOAL_POSITION = 116
XL320_GOAL_VELOCITY = 32
XM430_GOAL_VELOCITY = 112
LEN_PRO_PRESENT_POSITION = 2
LEN_XM430_PRESENT_POSITION = 4
PROTOCOL_VERSION = 2.0
BAUDRATE = 1000000
DEVICENAME = 'COM7'
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MOVING_STATUS_THRESHOLD = 20
kepala = [0,1,2]
kanan = [3,5,7,9,11,13]
kiri = [4,6,8,10,12,14]
kakikanan = [15,17,19.21,23,25]
kakikiri = [16,18,20,22,24,26]
DXL_XL320 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
DXL_LenganAtas = [13, 14]
DXL_Pinggang = [15, 16]
DXL_XM430 = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
dataMotion = []
urutan_gerak=0

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

groupSyncWrite_XM430                = GroupSyncWrite(portHandler, packetHandler, 112, 8)
groupSyncWrite_XL320                = GroupSyncWrite(portHandler, packetHandler, 30, 4)
groupSyncRead                       = GroupSyncRead(portHandler, packetHandler, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
groupSyncRead1                      = GroupSyncRead(portHandler, packetHandler, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION)
groupSyncRead_XM430                 = GroupSyncRead(portHandler, packetHandler, 132, 4)
# groupSyncReadcurrent_XM430          = GroupSyncRead(portHandler, packetHandler, 126, 2)
groupSyncRead_XL320                 = GroupSyncRead(portHandler, packetHandler, 37, 2)
groupSyncReadMove_XL320             = GroupSyncRead(portHandler, packetHandler, 49,1)
groupSyncReadMove_XM430             = GroupSyncRead(portHandler, packetHandler, 122,1)


def getIndexByNotElement(array,element):
    j = 0
    index = []
    for i in array:
        if(i != element):
            index.append(j)
        j+=1
    return index

def getNotValue(array,element):
    index = []
    for i in array:
        if(i != element):
            index.append(int(i))
    return index

def getNotValue_v2(array,element):
    j=0
    index_xl320 = []
    index_xm430 = []
    for i in array:
        if(i != element):
            if j in DXL_XM430 or j in DXL_Pinggang or j in DXL_LenganAtas:
                index_xm430.append(int(i))
            else:
                index_xl320.append(int(i))
        j+=1
    return index_xl320, index_xm430


def konversi(input, Ibawah, Iatas, Obawah, Oatas):
    return (input - Ibawah) / (Iatas - Ibawah) * (Oatas - Obawah)

def initialize_dynamixels():
    portHandler.openPort()
    portHandler.setBaudRate(BAUDRATE)
    groupSyncWrite_XL320.clearParam()
    groupSyncWrite_XL320.clearParam()
    for DXL1_ID in DXL_XL320 +  DXL_LenganAtas + DXL_Pinggang + DXL_XM430:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

def enable_dynamixels():
    for DXL1_ID in DXL_XL320 +  DXL_LenganAtas + DXL_Pinggang + DXL_XM430:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

def disable_dynamixels():
    for DXL1_ID in DXL_XL320 +  DXL_LenganAtas + DXL_Pinggang + DXL_XM430:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
    portHandler.closePort()

# def set_servo_velocity(servo_id, velocity):
#     for DXL1_ID in servo_id:
#         if DXL1_ID < 13:
#             addr = XL320_GOAL_VELOCITY
#             packetHandler.write2ByteTxRx(portHandler, servo_id, addr, velocity)
#         else:
#             addr = XM430_GOAL_VELOCITY
#             packetHandler.write4ByteTxRx(portHandler, servo_id, addr, velocity)

def bacaFile_v3(FILE_NAME):
    global MOTION_TIME_XM430, MOTION_TIME_XL320
    global MOTION_HEAD, MOTION_HAND, MOTION_FEET, MOTION_DXL, MOTION_DXL_XL320, MOTION_DXL_XM430
    
    file = open(FILE_NAME)
    csvreader = csv.reader(file)
    header = next(csvreader)

    MOTION_TIME_XM430 = []
    MOTION_TIME_XL320 = []
    MOTION_HEAD = []
    MOTION_HAND = []
    MOTION_FEET = []
    MOTION_DXL = []
    MOTION_DXL_XL320 = []
    MOTION_DXL_XM430 = []
    for row in csvreader:
        MOTION_TIME_XL320.append([row[i] for i in range(1, 13)])
        MOTION_TIME_XM430.append([row[i] for i in range(13, 27)])
        MOTION_DXL.append(row[27:])

        MOTION_DXL_XL320.append(row[:15])
        MOTION_DXL_XM430.append(row[15:30])

        MOTION_HEAD.append(row[3:6])
        MOTION_HAND.append(row[6:18])
        MOTION_FEET.append(row[18:30])
    
    file.close()

def gerak_by_motion_v6(NAMA_FILE, THRESHOLD_XL320=10, THRESHOLD_XM430=10, FILE2=None):
    global urutan_gerak

#    pub = rospy.Publisher('master_tp', Int32, queue_size=100)
#    rospy.Subscriber('bluetooth_data', Int32, bluetooth_callback)

    bacaFile_v3(NAMA_FILE)
    print(NAMA_FILE)

    for i in range(len(MOTION_DXL)):
        finish_head = finish_hands = finish_feet = 0
        timeout_head = timeout_hands = timeout_feet = 0
        i = int(i)
        
        DXL_IDS = getIndexByNotElement(MOTION_DXL[i], "-1")
        DXL_DEGREE = getNotValue(MOTION_DXL[i], "-1")
        DXL_DEGREE_XL320, DXL_DEGREE_XM430 = getNotValue_v2(MOTION_DXL[i], "-1")
        
#        print("MOTION :", NAMA_FILE, "STEP :", i)

        for ids, DXL_ID in enumerate(DXL_IDS):
            if DXL_ID >= 13:
                goal_pos = int(map(float(DXL_DEGREE[ids]), 0, 360, 0, 4096))
                goal_time = int(MOTION_TIME_XM430[i][DXL_ID - 13])
                Sync_Param = [
                    DXL_LOBYTE(DXL_LOWORD(int(goal_time))), 
                    DXL_HIBYTE(DXL_LOWORD(int(goal_time))),
                    DXL_LOBYTE(DXL_HIWORD(int(goal_time))), 
                    DXL_HIBYTE(DXL_HIWORD(int(goal_time))),
                    DXL_LOBYTE(DXL_LOWORD(int(goal_pos))), 
                    DXL_HIBYTE(DXL_LOWORD(int(goal_pos))),
                    DXL_LOBYTE(DXL_HIWORD(int(goal_pos))), 
                    DXL_HIBYTE(DXL_HIWORD(int(goal_pos)))
                ]
                dxl_addparam_result = groupSyncWrite_XM430.changeParam(DXL_ID, Sync_Param)
                if not dxl_addparam_result:
                    print("[ID:%03d] groupBulkWrite XM TIME addparam failed" % DXL_ID)
            else:
                goal_pos = int(map(float(DXL_DEGREE[ids]), 0, 300, 0, 1023))
                goal_time = int(MOTION_TIME_XL320[i][DXL_ID])
                Sync_Param = [
                    DXL_LOBYTE(DXL_LOWORD(int(goal_pos))), 
                    DXL_HIBYTE(DXL_LOWORD(int(goal_pos))),
                    DXL_LOBYTE(DXL_LOWORD(int(goal_time))), 
                    DXL_HIBYTE(DXL_LOWORD(int(goal_time)))
                ]
                dxl_addparam_result = groupSyncWrite_XL320.changeParam(DXL_ID, Sync_Param)
                if not dxl_addparam_result:
                    print("[ID:%03d] groupBulkWrite XL TIME addparam failed" % DXL_ID)

        dxl_comm_result = groupSyncWrite_XM430.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        dxl_comm_result = groupSyncWrite_XL320.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        urutan_gerak += 1

        while True:
            # if pause_gerakan:
            #     rospy.sleep(0.01)
            #     continue

            try:
                dxl_present_position_xm430 = []
                dxl_present_position_xl320 = []
                dxl_present_condition_xm430 = []
                dxl_present_condition_xl320 = []

                groupSyncReadMove_XL320.txRxPacket()
                groupSyncReadMove_XM430.txRxPacket()
                groupSyncRead_XM430.txRxPacket()
                groupSyncRead_XL320.txRxPacket()

                for DXL_ID in DXL_IDS:
                    if DXL_ID >= 13:
                        sudut = groupSyncRead_XM430.getData(DXL_ID, 132, 4)
                        dxl_present_position_xm430.append(map(sudut, 0, 4095, 0, 360))
                        dxl_present_condition_xm430.append(groupSyncReadMove_XM430.getData(DXL_ID, 122, 1))
                    else:
                        sudut = groupSyncRead_XL320.getData(DXL_ID, 37, 2)
                        dxl_present_position_xl320.append(map(sudut, 0, 1023, 0, 300))
                        dxl_present_condition_xl320.append(groupSyncReadMove_XL320.getData(DXL_ID, 49, 1))

                dxl_present_position_xl320 = np.asarray(dxl_present_position_xl320)
                dxl_present_position_xm430 = np.asarray(dxl_present_position_xm430)
                DXL_DEGREE_XL320 = np.asarray(DXL_DEGREE_XL320)
                DXL_DEGREE_XM430 = np.asarray(DXL_DEGREE_XM430)

                hasil_XL320 = dxl_present_position_xl320 - DXL_DEGREE_XL320
                hasil_XM430 = dxl_present_position_xm430 - DXL_DEGREE_XM430

                combined_condition = dxl_present_condition_xl320 + dxl_present_condition_xm430
                if all(j == 0 for j in combined_condition):
                    timeout_head += 1
                    timeout_hands += 1
                    timeout_feet += 1

                if not finish_head:
                    if all(abs(i) <= THRESHOLD_XL320 for i in hasil_XL320[0:3]) or timeout_head > 1:
                        finish_head = 1

                if not finish_hands:
                    hand_xl320_ok = all(abs(i) <= THRESHOLD_XL320 for i in hasil_XL320[3:13])
                    hand_xm430_ok = all(abs(i) <= THRESHOLD_XM430 for i in hasil_XM430[0:2])
                    if hand_xl320_ok and hand_xm430_ok or timeout_hands > 1:
                        finish_hands = 1

                if not finish_feet:
                    if all(abs(i) <= THRESHOLD_XM430 for i in hasil_XM430[2:]) or timeout_feet > 1:
                        finish_feet = 1

                if finish_head and finish_hands and finish_feet:
                    # pub.publish(urutan_gerak)
                    break
                # if handler.slave >= urutan_gerak:
                #     break
            except Exception as e:
                print(f"Error: {str(e)}")
            # rospy.sleep(0.001)
        urutan_gerak += 1
#        pub.publish(urutan_gerak)


def set_servo_velocity(servo_id, velocity):
    if servo_id < 13:
        addr = XL320_GOAL_VELOCITY
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, servo_id, addr, velocity)
    else:
        addr = XM430_GOAL_VELOCITY
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, servo_id, addr, velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result), "on ID", servo_id)
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error), "on ID", servo_id)


# def set_servo_velo(servo_id, velocity):
#     for DXL1_ID in servo_id:
#         if DXL1_ID < 13:
#             addr = XM430_GOAL_VELOCITY
#             dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL1_ID, addr, velocity)
#             if dxl_comm_result != COMM_SUCCESS:
#                 print("%s" % packetHandler.getTxRxResult(dxl_comm_result), "on ID", DXL1_ID)
#             elif dxl_error != 0:
#                 print("%s" % packetHandler.getRxPacketError(dxl_error), "on ID", DXL1_ID)

#         else:
#             addr = XL320_GOAL_VELOCITY
#             dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL1_ID, addr, velocity)
#             if dxl_comm_result != COMM_SUCCESS:
#                 print("%s" % packetHandler.getTxRxResult(dxl_comm_result), "on ID", DXL1_ID)
#             elif dxl_error != 0:
#                 print("%s" % packetHandler.getRxPacketError(dxl_error), "on ID", DXL1_ID)



def record_motion_gui(name, servo_id):
    motion_data = []
    print("Merekam motion", name)
    recording = True
    while recording:
        positions = []
        for DXL1_ID in servo_id:
            if DXL1_ID < 13:
                groupSyncRead.addParam(DXL1_ID)
            else:
                groupSyncRead1.addParam(DXL1_ID)
        dxl_comm_result = groupSyncRead.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        dxl_comm_result1 = groupSyncRead1.txRxPacket()
        if dxl_comm_result1 != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result1))

        for DXL1_ID in servo_id:
            if DXL1_ID < 13:
                if groupSyncRead.isAvailable(DXL1_ID, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION):
                    position = groupSyncRead.getData(DXL1_ID, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
                    positions.append(round(konversi(position, 0, 1023, 0, 300)))
            else:
                if groupSyncRead1.isAvailable(DXL1_ID, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION):
                    position = groupSyncRead1.getData(DXL1_ID, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION)
                    positions.append(round(konversi(position, 0, 4095, 0, 360)))
        motion_data.append(positions)
        groupSyncRead.clearParam()
        groupSyncRead1.clearParam()
        print(f"Step: {positions}")
        recording = False
        user_input = input("Tekan enter untuk merekam step selanjutnya atau ketik stop untuk menyimpan: ").strip().lower()
        if user_input == 'stop':
            recording = False
    return motion_data

def save_motion_data(name, motion_data, is_kaki):    
    path = f'motion_baru/{name}.csv'
    header = ['NAME'] + [f'T_XL320#{i}' for i in range(13)] + [f'T_XM430#{i}' for i in range(13, 27)] + [f'DXL#{i}' for i in range(27)]
    a1 = [name] + [100 for i in range(13)] + [1000 for i in range(13,27)]
    if is_kaki:
        a3 = [-1] * 15
    data_rows = []
    for step in motion_data:
        if is_kaki:
            row = a1 + a3 + step
        else:
            row = a1 + step
        data_rows.append(row)
    motion_df = pd.DataFrame(data_rows, columns=header)
    if not os.path.isdir('motion_baru'):
        os.mkdir('motion_baru')
    motion_df.to_csv(path, index=False)
    print(f'CSV file tersimpan ke {path}')

def play_motion_gui(motion_data, time_data, type):
    def display_step(index):
        step_data = motion_data[index]
        step_time = time_data[index]
        print(f"Step {index+1}/{len(motion_data)}")
        if type == "v6": 
            for DXL1_ID, position in enumerate(step_data):
                if DXL1_ID < 13:
                    position_value = int(konversi(int(position), 0, 300, 0, 1023))
                    time_value = step_time[DXL1_ID]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)), DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value))]
                    dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
                else:
                    position_value = int(konversi(int(position), 0, 360, 0, 4095))
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
                    position_value = int(konversi(int(position), 0, 300, 0, 1023))
                    time_value = step_time[0]
                    param_goal = [DXL_LOBYTE(DXL_LOWORD(position_value)), DXL_HIBYTE(DXL_LOWORD(position_value)), DXL_LOBYTE(DXL_LOWORD(time_value)), DXL_HIBYTE(DXL_LOWORD(time_value))]
                    dxl_addparam_result = groupSyncWrite_XL320.addParam(DXL1_ID, param_goal)
                    if dxl_addparam_result != True:
                        print("[ID:%03d] groupBulkWrite addparam failed" % DXL1_ID)
                        quit()
                else:
                    position_value = int(konversi(int(position), 0, 360, 0, 4095))
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
        label_step.configure(text=f"Step {index+1}/{len(motion_data)}")

    def next_step():
        nonlocal index
        if index < len(motion_data) - 1:
            index += 1
            display_step(index)
    def previous_step():
        nonlocal index
        if index > 0:
            index -= 1
            display_step(index)
    index = 0

    play_window = ctk.CTkToplevel(app)
    play_window.geometry("300x200")
    play_window.title("Melihat Motion")
    frame_play = ctk.CTkFrame(play_window)
    frame_play.pack(pady=20, padx=20, fill="both", expand=True)
    label_step = ctk.CTkLabel(frame_play, text="Step 1")
    label_step.pack(pady=10)
    button_previous = ctk.CTkButton(frame_play, text="Previous Step", command=previous_step)
    button_previous.pack(pady=10)
    button_next = ctk.CTkButton(frame_play, text="Next Step", command=next_step)
    button_next.pack(pady=10)
    display_step(index)

def update_csv_with_servo_position(name, step, servo_id):
    path = f'motion_baru/{name}.csv'
    if not os.path.exists(path):
        print("File motion tidak ditemukan.")
        return
    motion_data = pd.read_csv(path, header=None).values.tolist()
    if len(motion_data) <= step + 1:
        print("Step out of range.")
        return
    header = motion_data[0]
    if f'DXL#{servo_id}' not in header:
        print(f"Servo ID {servo_id} tidak ditemukan di dalam file")
        return
    servo_index = header.index(f'DXL#{servo_id}')
    if servo_id < 13:
        groupSyncRead.addParam(servo_id)
        dxl_comm_result = groupSyncRead.txRxPacket()
        if dxl_comm_result != 0:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        if groupSyncRead.isAvailable(servo_id, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION):
            position = groupSyncRead.getData(servo_id, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
            new_position = round(konversi(position, 0, 1023, 0, 300))
    else:
        groupSyncRead1.addParam(servo_id)
        dxl_comm_result = groupSyncRead1.txRxPacket()
        if dxl_comm_result != 0:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        if groupSyncRead1.isAvailable(servo_id, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION):
            position = groupSyncRead1.getData(servo_id, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION)
            new_position = round(konversi(position, 0, 4095, 0, 360))
    motion_data[step + 1][servo_index] = new_position
    pd.DataFrame(motion_data).to_csv(path, index=False, header=False)

def toggle_servo(servo_id, enable, name, step):
    for servo_loop in servo_id:
        addr_torque_enable = XL320_TORQUE_ENABLE if servo_loop < 13 else XM430_ADDR_TORQUE_ENABLE
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, servo_loop, addr_torque_enable, TORQUE_ENABLE if enable else TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print(f"Servo {servo_loop} berhasil {'dihidupkan' if enable else 'dimatikan'}")
            if enable:
                update_csv_with_servo_position(name, step, servo_loop)

def main():
    # initialize_dynamixels()
    global app
    app = ctk.CTk()
    app.geometry("550x550")
    app.title("AERORA Motion V2")

    def start_recording_kaki():
        name = entry_name.get()
        record_motion_gui(name, DXL_Pinggang + DXL_XM430, True)
    
    def start_recording_badan():
        name = entry_name.get()
        record_motion_gui(name, DXL_XL320 +  DXL_LenganAtas + DXL_Pinggang + DXL_XM430, False)
    
    # def view_motion():
    #     name = entry_name.get()
    #     path = f'motion_baru/{name}.csv'
    #     if os.path.exists(path):
    #         motion_data = pd.read_csv(path).drop(columns=['NAME'] + [f'T_XL320#{i}' for i in range(13)] + [f'T_XM430#{i}' for i in range(13, 27)] + [f'DXL#{i}' for i in range(27)]).values.tolist()
    #         play_motion_gui(motion_data)
    #     else:

    # def play():
    #     name = entry_name.get()
    #     path = f'motion_baru/{name}'.csv
    #     if os.path.exists(path):
    #         try:
    #             df = pd.read_csv(path)
    #             dxl_columns = [f'DXL#{i}' for i in range(27)]
    #             if all(col in df.columns for col in dxl_columns):
    #                 motion_data = df[dxl_columns].values.tolist()
    #                 play_motion_gui(motion_data)
    #             else:
    #                 print("File tidak memiliki semua kolom yang diperlukan (DXL#0 hingga DXL#26).")
    #         except Exception as e:
    #             print(f"Terjadi kesalahan saat memuat file: {e}")
    #     else:
    #         print("File motion tidak ditemukan. Pastikan nama file sesuai dan berada di folder 'motion_baru'.")
    #     plays = (f"{entry_name}", 10,5)

    def view_motion_baru():
        name = entry_name.get()
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
                    motion_data = df[dxl_columns].values.tolist()
                    time_data = df[time_columns_v6].values.tolist()
                    play_motion_gui(motion_data, time_data, 'v6')
                elif all(col in df.columns for col in cek_columns):
                    motion_data = df[dxl_columns].values.tolist()
                    time_data = df[time_columns].values.tolist()
                    play_motion_gui(motion_data, time_data, 'anjay')
                else:
                    print("File tidak memiliki semua kolom yang diperlukan (DXL#0 hingga DXL#26).")
            except Exception as e:
                print(f"Terjadi kesalahan saat memuat file: {e}")
        else:
            print("File motion tidak ditemukan. Pastikan nama file sesuai dan berada di folder 'motion_baru'.")


    def view_motion_lama():
        name = entry_name.get()
        path = f'motion_baru/{name}.csv'
        if os.path.exists(path):
            motion_data = pd.read_csv(path).drop(columns=['NAME', 'T_XL320', 'T_XM430']).values.tolist()
            play_motion_gui(motion_data)
        else:
            print("File motion tidak ditemukan.")

    def toggle_servo_state():
        name = entry_name.get()
        step = int(entry_step.get())
        servo_id = entry_servo_id.get().split(',')
        servo_id = [int(servo) for servo in servo_id]
        state = toggle_var.get()
        toggle_servo(servo_id, state == 'on', name, step)

    def record_motion_gui(name, servo_id, is_kaki):
        motion_data = []
        def capture_step():
            positions = []
            for DXL1_ID in servo_id:
                if DXL1_ID < 13:
                    groupSyncRead.addParam(DXL1_ID)
                else:
                    groupSyncRead1.addParam(DXL1_ID)
            dxl_comm_result = groupSyncRead.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            dxl_comm_result1 = groupSyncRead1.txRxPacket()
            if dxl_comm_result1 != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result1))
            for DXL1_ID in servo_id:
                if DXL1_ID < 13:
                    if groupSyncRead.isAvailable(DXL1_ID, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION):
                        position = groupSyncRead.getData(DXL1_ID, XL320_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
                        positions.append(round(konversi(position, 0, 1023, 0, 300)))
                else:
                    if groupSyncRead1.isAvailable(DXL1_ID, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION):
                        position = groupSyncRead1.getData(DXL1_ID, XM430_PRESENT_POSITION, LEN_XM430_PRESENT_POSITION)
                        positions.append(round(konversi(position, 0, 4095, 0, 360)))
            motion_data.append(positions)
            groupSyncRead.clearParam()
            groupSyncRead1.clearParam()
            print(f"Step: {positions}")
            label_steps.configure(text=f"Step Terekam: {len(motion_data)}")
        
        def finish_recording():
            save_motion_data(name, motion_data, is_kaki)
            record_window.destroy()
        
        def servo_badan():
            if switch_var_badan.get() == "on":
                for DXL1_ID in DXL_XL320 + DXL_LenganAtas:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in DXL_XL320 + DXL_LenganAtas:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        def servo_kaki():
            if switch_var_kaki.get() == "on":
                for DXL1_ID in DXL_Pinggang + DXL_XM430:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in DXL_Pinggang + DXL_XM430:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        def servo_kakikanan():
            if switch_var_kakikanan.get() == "on":
                for DXL1_ID in kakikanan:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in kakikanan:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        def servo_kakikiri():
            if switch_var_kakikiri.get() == "on":
                for DXL1_ID in kakikiri:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in kakikiri:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        def servo_tangankanan():
            if switch_var_t_kanan.get() == "on":
                for DXL1_ID in kanan:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in kanan:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
                    
        def servo_tangankiri():
            if switch_var_t_kiri.get() == "on":
                for DXL1_ID in kiri:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in kiri:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        def servo_kepala():
            if switch_var_kepala.get() == "on":
                for DXL1_ID in kepala:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))
            else:
                for DXL1_ID in kepala:
                    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL1_ID, XL320_TORQUE_ENABLE if DXL1_ID < 13 else XM430_ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % packetHandler.getRxPacketError(dxl_error))

        switch_var_badan = ctk.StringVar(value="on")
        switch_var_kaki = ctk.StringVar(value = "on")
        switch_var_t_kanan = ctk.StringVar(value="on")
        switch_var_t_kiri = ctk.StringVar(value="on")
        switch_var_kepala = ctk.StringVar(value="on")
        switch_var_kakikanan = ctk.StringVar(value="on")
        switch_var_kakikiri = ctk.StringVar(value="on")
        record_window = ctk.CTkToplevel(app)
        record_window.geometry("600x600")
        record_window.title("Merekam Motion")
        frame_record = ctk.CTkFrame(record_window)
        frame_record.pack(pady=20, padx=20, fill="both", expand=True)
        label_steps = ctk.CTkLabel(frame_record, text="Step Terekam: 0")
        label_steps.pack(pady=2)
        button_capture = ctk.CTkButton(frame_record, text="Rekam Step", command=capture_step)
        button_capture.pack(pady=2)
        button_finish = ctk.CTkButton(frame_record, text="Simpan Motion", command=finish_recording)
        button_finish.pack(pady=2)
        switch_badan = ctk.CTkSwitch(frame_record, text="ON Servo 0-14", command=servo_badan, variable=switch_var_badan, onvalue="on", offvalue="off")
        switch_badan.pack(padx=20, pady=10)
        switch_kaki = ctk.CTkSwitch(frame_record, text="ON Servo 15-26", command=servo_kaki, variable=switch_var_kaki, onvalue="on", offvalue="off")
        switch_kaki.pack(pady=2)
        switch_t_kanan = ctk.CTkSwitch(frame_record, text="ON Servo Tangan Kanan", command=servo_tangankanan, variable=switch_var_t_kanan, onvalue="on", offvalue="off")
        switch_t_kanan.pack(pady=2)
        switch_t_kiri = ctk.CTkSwitch(frame_record, text="ON Servo Tangan Kiri", command=servo_tangankiri, variable=switch_var_t_kiri, onvalue="on", offvalue="off")
        switch_t_kiri.pack(pady=2)
        switch_kepala = ctk.CTkSwitch(frame_record, text="ON Servo Kepala", command=servo_kepala, variable=switch_var_kepala, onvalue="on", offvalue="off")
        switch_kepala.pack(pady=2)
        switch_kakikanan = ctk.CTkSwitch(frame_record, text="ON Servo Kaki Kanan", command=servo_kakikanan, variable=switch_var_kakikanan, onvalue="on", offvalue="off")
        switch_kakikanan.pack(pady=2)
        switch_kakikiri = ctk.CTkSwitch(frame_record, text="ON Servo Kaki Kiri", command=servo_kakikiri, variable=switch_var_kakikiri, onvalue="on", offvalue="off")
        switch_kakikiri.pack(pady=2)

    frame = ctk.CTkFrame(app)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    entry_name = ctk.CTkEntry(frame, placeholder_text="Masukkan nama motion")
    entry_name.pack(pady=10)
    entry_step = ctk.CTkEntry(frame, placeholder_text="Masukkan nomor step")
    entry_step.pack(pady=10)
    entry_servo_id = ctk.CTkEntry(frame, placeholder_text="Masukkan servo ID")
    entry_servo_id.pack(pady=10)
    toggle_var = ctk.StringVar(value="off")
    toggle_servo_on = ctk.CTkRadioButton(frame, text="On", variable=toggle_var, value="on")
    toggle_servo_on.pack(pady=5)
    toggle_servo_off = ctk.CTkRadioButton(frame, text="Off", variable=toggle_var, value="off")
    toggle_servo_off.pack(pady=5)
    record_kaki_button = ctk.CTkButton(frame, text="Rekam Motion Kaki", command=start_recording_kaki)
    record_kaki_button.pack(pady=10)
    record_badan_button = ctk.CTkButton(frame, text="Rekam Motion Badan", command=start_recording_badan)
    record_badan_button.pack(pady=10)
    view_motion_button = ctk.CTkButton(frame, text="Lihat Motion", command=view_motion_baru)
    view_motion_button.pack(pady=10)
    view_motion_lama = ctk.CTkButton(frame, text="Lihat Motion Lama", command=view_motion_lama)
    view_motion_lama.pack(pady=10)
    view_motion_v6 = ctk.CTkButton(frame, text="Lihat Motion v6", command=view_motion_baru)
    view_motion_v6.pack(pady=10)
    toggle_servo_button = ctk.CTkButton(frame, text="Toggle Servo", command=toggle_servo_state)
    toggle_servo_button.pack(pady=10)
    app.mainloop()
    disable_dynamixels()

if __name__ == "__main__":
    main()
