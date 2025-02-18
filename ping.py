#Prepared By Althaf Aman
#C23060007
#Note: Thing program cannot execute without internet


import os
import sys
import socket
import struct
import time


ICMP_REQUEST = 8

def checksum(source_string):
    """Calculates checksum for ICMP packet"""
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum += this_val
        sum &= 0xfffffffff
        count += 2

    if count_to < len(source_string):
        sum += source_string[-1]
        sum &= 0xffffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    answer = ~sum
    answer &= 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(seq_number):
    """Creating an ICMP packet with a checksum"""
    header = struct.pack("bbHHh", ICMP_REQUEST, 0, 0, 1, seq_number)
    data = struct.pack("d", time.time())  # Using current time as data
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_REQUEST, 0, socket.htons(my_checksum), 1, seq_number)
    return header + data

def send_ping(dest_addr, seq_number, sock):
    """Sending an ICMP request"""
    packet = create_packet(seq_number)
    sock.sendto(packet, (dest_addr, 1))

def receive_ping(sock, timeout):
    """Receive an ICMP reply"""
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            return None, None, None

        sock.settimeout(timeout - elapsed_time)
        try:
            packet, addr = sock.recvfrom(1024)
            icmp_header = packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
            if type == 0:  # Echo Reply
                return time.time() - struct.unpack("d", packet[28:])[0]
        except socket.timeout:
            return None, None, None

def ping(host):
    """Ping a host with ICMP requests"""
    try:
        dest_addr = socket.gethostbyname(host)
        print(f"Pinging {host} ({dest_addr}) in Python:")

        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        seq_number = 1

        for _ in range(4):  # Send 4 ping requests
            send_ping(dest_addr, seq_number, sock)
            delay = receive_ping(sock, 1)
            if delay is None:
                print("Request timed out.")
            else:
                print(f"Reply from {dest_addr}: time={round(delay * 1000, 2)}ms")

            seq_number += 1
            time.sleep(1)

        sock.close()

    except socket.gaierror:
        print("Error: Unable to resolve host.")
    except PermissionError:
        print("Error: Pls Run the script as Administrator.")

if __name__ == "__main__":
    target_host = input("Ping a Host: ")
    ping(target_host)
