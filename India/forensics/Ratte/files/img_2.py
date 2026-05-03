import scapy.all as scapy

packets = scapy.rdpcap("ratte.pcap")

xor_key = 0x42  
flag_encrypted = b""

for pkt in packets:

    if pkt.haslayer(scapy.TCP) and pkt.haslayer(scapy.Raw):
        payload = pkt[scapy.Raw].load

        if payload.startswith(b"\xcc"):
            length = payload[2] 
            data = payload[3:3+length]
            flag_encrypted += data

# Дешифруем всё накопленное
flag = "".join([chr(b ^ xor_key) for b in flag_encrypted])
print(f"Найден флаг: {flag}")
