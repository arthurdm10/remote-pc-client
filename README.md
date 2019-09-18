python main.py <server:port> <key>

To register this PC:
python main.py register <server:port> <username> <password> [key]
<server:port>: Remote server
<username> <password>: Credentials used to connect to remote server
[key]: Used to connect to this PC - If not provided, a random key will be generated

To register a user:
python main.py register-user <server:port> <username> <password> <key>
<server:port>: Remote server
<username> <password>: Users credentials used to connect to this PC
<key>: The key used when this PC was registered

To set users permissions:
python main.py user-permissions <permissions.json> <server:port> <key>
<permissions.json>: File with users permissions
<server:port>: Remote server
<key>: The key used when this PC was registered

Python version: 3.6.8
