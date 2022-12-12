import socket 
import sys 
import os 
import logging 
from time import sleep 
from common import * 
from tkinter import * 
 
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)-03d : %(message)s', datefmt='%H:%M:%S')
s = None 
R_n = 0 
pbuffer = [None] * SRP_WINDOW_SIZE 
nack_sent, ack_needed = False, False 
data_recvd = [] 
nack_ens=[False for i in range(0,8)]
 
def send_nack(sno):     
    pkt = Packet(seq_no=sno, data=b'', ptype=Packet.type_nack)     
    send_packet(s,pkt)
    logging.info('[NACK] : %s' %pkt)     
    str2 = "[NACK]   : NACK sent" + str(pkt)+'\n' 
    text.insert(END,str2) 
    window.update() 
 
def send_ack(sno):     
    pkt = Packet(seq_no=sno, data=b'', ptype=Packet.type_ack)     
    send_packet(s,pkt)     
    logging.info('[ACK] : %s' %pkt)     
    str2 = "[ACK]   : ACK sent" + str(pkt)+'\n'     
    text.insert(END,str2) 
    window.update() 
 
 
def is_valid_seqno(seqno): 
    a=seqno in [(R_n + i) % (MAX_SEQ_NO + 1) for i in range(SRP_WINDOW_SIZE)]     
    return a 
 
def to_network_layer(char):     
    data_recvd.append(char) 
    print("Data to network layer :",data_recvd) 
 
def main(): 
 
    global nack_sent, ack_needed, R_n 
    n=0     
    while 1:         
        pkt = recv_packet(s)       
        if pkt == 0 :             
            break         
        if pkt.is_corrupt() and pbuffer[pkt.seq_no%SRP_WINDOW_SIZE] is None: 
            if pkt.seq_no not in [(R_n - i) % (MAX_SEQ_NO + 1) for i in range(1,SRP_WINDOW_SIZE)]: 
                print("Packet is corrupted!")                 
                nack_ens[pkt.seq_no]=True                 
                send_nack(pkt.seq_no) 
                continue  
        if pkt.seq_no in [(R_n - i) % (MAX_SEQ_NO + 1) for i in range(1,SRP_WINDOW_SIZE+1)]: 
            print("Resending Ack!")             
            send_ack(pkt.seq_no) 
            continue         
        elif pkt.seq_no != R_n and not nack_ens[pkt.seq_no]:             
            print("Unordered Packet!")             
            send_nack(R_n)             
            nack_ens[pkt.seq_no]=True             
            nack_sent = True         
        if is_valid_seqno(pkt.seq_no):             
            if pbuffer[pkt.seq_no % SRP_WINDOW_SIZE] is None:                 
                pbuffer[pkt.seq_no % SRP_WINDOW_SIZE] = pkt                 
                logging.info('[RECV] : %s' %pkt) 
                str3 = "[RECV]   : Received Packet" + str(pkt)+'\n' 
                text.insert(END,str3)                 
                window.update()                 
                send_ack(pkt.seq_no)                 
                nack_ens[pkt.seq_no]=False                 
                while pbuffer[R_n % SRP_WINDOW_SIZE]: 
                    data = pbuffer[R_n % SRP_WINDOW_SIZE].data                     
                    to_network_layer(data) 
                    pbuffer[R_n % SRP_WINDOW_SIZE] = None 
                    R_n = (R_n + 1) % (MAX_SEQ_NO + 1)          
        sleep(.75) 
 
def connect():     

    global data_recvd,s 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
    host="172.22.61.149"
    s.connect((host,8000))
    print("Connection Established\n")     
    text.insert(END, "Connection Established\n")     
    window.update()     
    try: 
        main()     
    except ConnectionResetError: 
        pass 
    logging.info('Transfer complete. Received \'%s\'' %''.join(data_recvd))     
    str6="Recieved the message"+ str(data_recvd)
    text.insert(END,str6)
    window.update()
    sleep(10)     
    sys.exit(0) 
 
if __name__=='__main__':     
    window = Tk()  
    window.title("Receiver")   
    text = Text(window)     
    text.grid(row = 2, column = 0) 
    button = Button(window,text="Connect",command=connect) 
    button.grid(row = 1, column = 0)     
    window.mainloop() 
