# Steps to Set Up stunnel with SSL/TLS

Install and configure stunnel
You need to install stunnel on the same machine where the relay resides, then set it up to manage the inbound SSL connections and forward data received to the relay.

# 1. Install stunnel with the following command

```bash
sudo apt-get install stunnel4
```

Enable stunnel by editing the file and setting ENABLED to 1.

```bash
sudo vi /etc/default/stunnel4
```

or 

```bash
sudo nano /etc/default/stunnel4
```



# 2. Generate Pem and Crt

 # 2.1 Generate Certificate Signing Request (CSR)

```bash
sudo openssl req -new -key /etc/stunnel/server.key -out /etc/stunnel/server.csr
```

You will be prompted to enter some details such as
Country Name (2 letter code)
State or Province Name
Organization Name
Common Name (e.g., server FQDN or IP address)

 # 2.2 Create a Self-Signed Certificate
After generating the CSR, use the following command to create a self-signed certificate

```bash
sudo openssl x509 -req -in /etc/stunnel/server.csr -signkey /etc/stunnel/server.key -out /etc/stunnel/server.crt
```

 # 2.3 Combine the Private Key and Certificate into PEM format
For stunnel to use both the private key and certificate in one file, combine them into a single PEM file
```bash
sudo bash -c 'cat /etc/stunnel/server.key /etc/stunnel/server.crt > /etc/stunnel/stunnel.pem'
```

# 3. Open the stunnel configuration file for editing

```bash
vi /etc/stunnel/stunnel.conf
```
or
```bash
sudo nano /etc/stunnel/stunnel.conf
```

Use this conf

```bash
; **************************************************************************
; * Global options                                                         *
; **************************************************************************
 
; It is recommended to drop root privileges if stunnel is started by root
setuid = stunnel4
setgid = stunnel4
 
; PID file is created inside the chroot jail (if enabled)
pid = /var/run/stunnel4/stunnel.pid
 
; Debugging stuff (may be useful for troubleshooting)
;foreground = yes
debug = debug
output = /var/log/stunnel4/stunnel.log
 
[epo]
client = no
accept = 6514
connect = 127.0.0.1:13031
cert = /etc/stunnel/stunnel.pem
verifyChain = yes
verifyPeer = yes
CAfile = /etc/stunnel/server.crt
```
Restart stunnel4
```bash
sudo systemctl restart stunnel4
```
# 3. Check Status
Check Status
```bash
sudo systemctl status stunnel4
```
Check Port 
```bash
sudo ss -lntp | grep 6520
```


Jacked
