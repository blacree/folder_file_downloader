# upload_to_client
Download all the files in a folder including those contained in sub-folders

This is a custom python script that helps to download the files contained in a folder and it's subfolders.
This is very useful when you have terminal access to a target computer and do not want to download the contents of a folder one by one.

The script is run as a server on the computer which contains the files and run as client on the computer which wants to receive the files.
More than one computer can connect to the server as a client to receive the files to be downloaded. 

Run "python upload_to_client.py" to view the instructions on how to use this script.

Either of the scripts upload_to_client.py or upload_to_client_linux.py can be run as server on both windows and linux, but only
upload_to_client_linux.py should be run as client on a linux computer and upload_to_client.py as client on a windows computer.
