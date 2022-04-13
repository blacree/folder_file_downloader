# folder_file_downloader
Run "python upload_to_client.py" to view instructions.

This script implements a server client model to send files across a network

It can be run as either a server or a client.

    - Server: sends files to the client

    - Client: receives files from the server

#### Features:-
* Send a single file
* Send multiple files (Directory - Including files in its sub-folders
* Multiple clients can connect to server to receive the same set of files
* Validates each file using hash
* Works on both linux and windows