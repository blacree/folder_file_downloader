import sys
import subprocess
import optparse
import socket
import threading
import os
import time
#import multiprocessing
import hashlib
#import concurrent.futures as threadzz
from datetime import datetime

server_boolean = False
target_boolean = False
directory_path = []


# How to use this script
def usage():
    print("For client mode run:")
    print("[+] python script.py -t [ip-address] -p [port-number]")
    print('[*] Example: python script.py -t 127.0.0.1 -p 9999')
    print("\nFor server mode run:")
    print("[+] python script.py -l -p [port-number] -f [folder-path] -s [speed(no)] -c [clients[no]]")
    print('[*] Example: python script.py -l -p 9999 -f /root/Documents -s [no] -c 5')
    print("Note: If no port is provided for the server the default port used is 9999")
    print("Note: If no speed value is provided for the server the default speed used is 1")
    print("Note: If no value is provided for no of clients for the server the default value is 1")
    print("Note: Please do not provide more than one forward slash for each one in the path provided")
    print("\n[*] Options -t and -p are compulsory for creating the client instance")
    print("[*] Options -l and -f are compulsory for creating the server instance")
    print("[*]Note: If you want to repeat the dowload process for the same set of files deleting the downloaded copies increases the probability of succesfull file transfer.")


# Start the client
def start_client_instance(target, port):
    check_filename = b'$$file_name'
    #check_for_next = b'$$move_to_next' 
    sending_complete = b'$$sending_complete'
    hash_identifier = b'.$$hashh'
    file_sent_complete = b'$$file_complete'
    file_and_hash = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[*] Connecting to server...")
    try:
        # Connect to server
        server.connect((target, port))
        print()
        print('[+] Connection to server successful...')
        print('[+] Downloading contents from server...')
        print()
    except:
        print("Failed to connect to server.")
        print("Exiting...")
        exit()

    # Receive the files from the server
    while True:
        data = server.recv(4096)

        if sending_complete in data:
            break

        if check_filename in data:
            filename = b''
            received_file = data.split(b'.')
            filename = received_file[0]
            for value in received_file:
                if value in filename:
                    continue
                if value == received_file[-2]:
                    filename = filename + b'.' + value
                    break
                filename = filename + b'.' + value 
            print()
            print(b'[*] Creating file: ' + filename)
            print('[*]Receiving content...')
            opener = open(filename, 'wb')
            continue
        if hash_identifier in data:
            main_hash = data.split(b'.')[0]
            print('Received hash for file: ' + str(main_hash))
            file_and_hash[filename] = main_hash
            continue
        if file_sent_complete in data:
            print(b'[+]'+ filename + b' received successfully.')
            opener.close()
        try:
            opener.write(data)
        except:
            continue      
    

    # Close the connection after receiving all files
    try:
        server.close()
        print()
        print('[+]Download operation completed successfully.')
    except:
        print()
        print('[+]Download operation completed successfully.')
    
    # Generate hash for each received file
    dowloaded_file_hash = {}
    for word in file_and_hash:
        File = open(word, 'rb')
        content = File.read()
        File.close()
        hashing = hashlib.md5()
        hashing.update(content)
        hash_result = hashing.hexdigest()
        dowloaded_file_hash[word] = hash_result.encode()
    
    # Compare the generated hash with the hash transmitted by the server, so as to check for errors
    for word in file_and_hash:
        print()
        print(word)
        print('Received hash: ' + str(file_and_hash[word]) + '\nCalculated hash: ' + str(dowloaded_file_hash[word]))
        if file_and_hash[word] == dowloaded_file_hash[word]:
            print('[+]Hash matched succesfully.')
        else:
            print('[-]Hashes do not match. The file was not received properly.')

    print()    
    print('[+]Exiting...')



# Start the server
def start_server_instance(port, directory_content, no_client, dir_list):
    target = '0.0.0.0'
    main_content = ''
    sending_complete = '$$sending_complete'
    file_sent_complete = '$$file_complete'
    global directory_path
    connected_devices = []
    addresses_connected_devices = []

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    # Set the maximum number of clients to be connected to the server. Server does not start sending until all clients have connected
    server.listen(no_client)

    # If the maximum client is one
    if no_client == 1:
        client_socket, addr = server.accept()

        # Calculate the start time
        if client_socket:
            print()
            print('[+] Client ' + str(addr) + ' has connected...')
            print('[+] Sending files to client...')
            now = datetime.now()
            start_time = now.strftime("%H:%M:%S")
            print("Start Time =", start_time)
            print()

        # Send each file in the list one by one. Hash of the file is also generated and sent to client.
        for fille in directory_content:
            hashing = hashlib.md5()
            main_file = open(fille, 'rb')
            main_content = main_file.read()
            main_file.close()
            name_of_file = fille.split("/")[-1]
            filename = name_of_file + '.$$file_name'
            time.sleep(0.3)
            client_socket.send(filename.encode())
            hashing.update(main_content)
            hash_result = hashing.hexdigest()
            sent_hash = hash_result + '.$$hashh'
            time.sleep(0.3)
            client_socket.send(sent_hash.encode())
            print()
            print("[*]Sending " + fille + ' to client')
            print("[*]File Hash: " + hash_result)
            time.sleep(0.3)
            client_socket.send(main_content)
            print("[+]"+fille + ' sent successfully.')
            time.sleep(0.3)
            client_socket.send(file_sent_complete.encode())
        time.sleep(0.3)
        client_socket.send(sending_complete.encode())
        print()
        print("File transfer complete for client: " + str(addr))
        now = datetime.now()
        final_time = now.strftime("%H:%M:%S")
        # Print the start and End time
        print("Start time: " + start_time)
        print("Time of completion", final_time)

        # Close connection
        if client_socket:
            client_socket.close()
            print()
            print("[*]Exiting...")
        else:
            print()
            print("[*]Exiting...")
    else:
        # If more than one client connects to server
        while True:
            client_socket, addr = server.accept()
            if client_socket:
                connected_devices.append(client_socket)
                addresses_connected_devices.append(addr)
                print()
                print("[+] Client " + str(addr) + " has connected.")
            if len(connected_devices) == no_client:
                break
        
        print("\nSending files to connected clients...")
        now = datetime.now()
        start_time = now.strftime("%H:%M:%S")
        print("Start Time =", start_time)
        print()
        # Send each file to every client.
        for fille in directory_content:
            address_counter = 0
            for client_socket in connected_devices:
                hashing = hashlib.md5()
                main_file = open(fille, 'rb')
                main_content = main_file.read()
                main_file.close()
                name_of_file = fille.split("/")[-1]
                filename = name_of_file + '.$$file_name'
                time.sleep(0.3)
                client_socket.send(filename.encode())
                hashing.update(main_content)
                hash_result = hashing.hexdigest()
                sent_hash = hash_result + '.$$hashh'
                time.sleep(0.3)
                client_socket.send(sent_hash.encode())
                print()
                print("[*]Sending " + fille + ' to client ' + str(addresses_connected_devices[address_counter]))
                print("[*]File Hash: " + hash_result)
                time.sleep(0.3)
                client_socket.send(main_content)
                print("[+]"+fille + ' sent successfully.')
                time.sleep(0.3)
                client_socket.send(file_sent_complete.encode())
                address_counter += 1
        address_counter = 0

        # Close the connection between each client
        for client_socket in connected_devices:
            client_socket.send(sending_complete.encode())
            address = addresses_connected_devices[address_counter]
            print()
            print("File transfer complete for client: " + str(address[0]))
            address_counter += 1
        for client_socket in connected_devices:
            try:
                client_socket.close()
            except:
                continue
        now = datetime.now()
        final_time = now.strftime("%H:%M:%S")
        print("\nStart time: " + start_time)
        print("Time of completion", final_time)
        print("[*]Exiting...")


def main():
    global server_boolean
    global target_boolean
    port_c = False
    target_c = False
    directory_path_c = False
    speed_c = False
    target = ''
    port = 9999
    no_client = 1
    client_c = False
    global directory_path
    directory_content = []
    speed = 1

    # Check if the appropriate options are used
    if len(sys.argv[1:]):
        argumentlist = sys.argv[1:]
        if '-l' in argumentlist and '-t' in argumentlist:
            print("[-] You cannot use options -t and -l together\n")
            usage()
            exit()
        if ('-l' not in argumentlist) and ('-t' not in argumentlist):
            print("[-] Options '-l' or '-t' must be provided for server instance or client instance respectively. \n")
            usage()
            exit()
        if '-l' in argumentlist and ('-f' not in argumentlist):
            print("[-] Both options '-l' and '-f' are compulsory to start the server.\n")
            usage()
            exit()
        if '-t' in argumentlist and ('-p' not in argumentlist):
            print("[-] Both options '-t' and '-p' are compulsory to start a client instance.\n")
            usage()
            exit()
    else:
        usage()
        exit()

    
    # Check if script would run as a client or as a server and collect the respective options passed to the script
    # Make sure that the needed information is passed for server instance or client instance.
    if '-l' in argumentlist:
        server_boolean = True
    else:
        if '-t' in argumentlist:
            target_boolean = True
    
    if target_boolean:
        if len(sys.argv[1:]) < 4:
            print('[-] Incomplete arguments provided for client instance\n')
            usage()
        if len(sys.argv[1:]) > 4:
            print('[-] Too  arguments provided for client instance\n')
            usage()
            exit()

    if server_boolean:
        if len(sys.argv[1:]) < 3:
            print('[-] Incomplete arguments provided for server instance.\n')
            usage()
        if len(sys.argv[1:]) > 9:
            print('[-] Too many arguments provided for server instance\n')
            usage()
            exit()
    
    
    if target_boolean:
        for word in argumentlist:
            if 't' in word:
                target_c = True
                continue
            if target_c:
                target = word
                break
        for word in argumentlist:
            if '-p' in word:
                port_c = True
                continue
            if port_c:
                try:
                    port = int(word)
                    break
                except:
                    port = port
                    break

    if server_boolean:
        for word in argumentlist:
            if '-p' in word:
                port_c = True
                continue
            if port_c:
                try:
                    port = int(word)
                    break
                except:
                    port = port
                    break
        for word in argumentlist:
            if '-f' in word:
                directory_path_c = True
                continue
            if directory_path_c:
                directory_path = word
                break 
        for word in argumentlist:
            if '-s' in word:
                speed_c = True
                continue
            if speed_c:
                try:
                    speed = int(word)
                    break
                except:
                    speed = speed
                    break
        for word in argumentlist:
            if '-c' in word:
                client_c = True
                continue
            if client_c:
                try:
                    no_client = int(word)
                    break
                except:
                    no_client = no_client
                    break

        
        # Collect all file names in the folder, including those in subfolders and store them in a list
        test_for_dir = []
        for dir_file in os.listdir(directory_path):
            file_path = directory_path + "/" + dir_file
            test_for_dir.append(file_path)
        
        dir_list = []
        test_if_done = False

        while True:
            if test_if_done == True:
                break
            counter = 0
            for fille in test_for_dir:
                if os.path.isdir(fille):
                    dir_list.append(fille)
                    for file_ in os.listdir(fille):
                        file_path = fille + "/" + file_
                        test_for_dir.append(file_path)                    
                    test_for_dir.remove(fille)
                    counter += 1
                else:
                    if fille not in directory_content:
                        directory_content.append(fille)
            if counter > 0:
                test_if_done = False
            else:
                if counter == 0:
                    test_if_done = True
        
        



    # Start the server
    if server_boolean:
        print(directory_content)
        start_server_instance(port, directory_content, no_client, dir_list)

        # threadspeed = threadzz.ThreadPoolExecutor(speed)
        # threadspeed.submit(start_server_instance, port, directory_content)
        # threadspeed.shutdown(wait=True)
        
        # t = threading.Thread(target=start_server_instance, args=(port, directory_content))
        # t.start()

    # Start the client and connect to server. Server has to be running before starting client
    if target_boolean:
        start_client_instance(target, port)
        

# Start main function.
main()