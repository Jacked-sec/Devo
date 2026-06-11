# Linux Log Forwarding to Devo Relay Using rsyslog

## Overview

This document explains how to configure `rsyslog` on Linux to forward system log events to a Devo Relay over TCP.

This method is suitable when forwarding Linux system logs from internal servers to a Devo Relay.

## Architecture

```text
Linux Server
     ↓
  rsyslog
     ↓ TCP
 Devo Relay
     ↓
 Devo Cloud
```

## Expected Devo Table

The forwarded logs are expected to appear in Devo under:

```text
box.unix
```

---

## Prerequisites

### Linux Server

- Linux server with `rsyslog` installed
- Network connectivity to Devo Relay
- Permission to edit files under `/etc/rsyslog.d/`
- Permission to restart `rsyslog`

### Devo Relay

- Devo Relay installed and running
- Relay listener port is enabled
- Firewall allows inbound traffic from Linux server to relay port

Example relay port:

```text
13011/tcp
```

---

## 1. Check rsyslog Service

Check whether `rsyslog` is running:

```bash
sudo systemctl status rsyslog
```

If it is not installed:

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install rsyslog -y
```

### RHEL / CentOS / Rocky Linux

```bash
sudo yum install rsyslog -y
```

Enable and start service:

```bash
sudo systemctl enable rsyslog
sudo systemctl start rsyslog
```

---

## 2. Configure `/etc/rsyslog.conf`

It is recommended to keep `/etc/rsyslog.conf` simple and use only the include directive.

File:

```text
/etc/rsyslog.conf
```

Recommended content:

```conf
#
# http://www.rsyslog.com/doc/
#

# Include all config files in /etc/rsyslog.d/
include(file="/etc/rsyslog.d/*.conf")
```

This helps prevent duplicated or conflicting rsyslog rules.

---

## 3. Create Devo rsyslog Configuration Files

Create two files under:

```text
/etc/rsyslog.d/
```

Files:

```text
/etc/rsyslog.d/00-devo.conf
/etc/rsyslog.d/49-devo.conf
```

---

## 4. Create `/etc/rsyslog.d/00-devo.conf`

This file contains general module and working directory settings.

```bash
sudo nano /etc/rsyslog.d/00-devo.conf
```

Add the following configuration:

```conf
module(
    load="imfile"
    mode="inotify"
)

module(
    load="immark"
    interval="60"
)

module(
    load="imuxsock"
    SysSock.RateLimit.Interval="0"
)

global(
    workDirectory="/var/spool/rsyslog"
)
```
or if error imuxsock and imfile
```bash
module(
    load="immark"
    interval="60"
)

global(
    workDirectory="/var/spool/rsyslog"
)
```
---

## 5. Prepare rsyslog Work Directory

Check which user runs `rsyslog`:

```bash
ps -ouser= $(pgrep rsyslogd)
```

Create the working directory:

```bash
sudo mkdir -p /var/spool/rsyslog
```

If `rsyslog` runs as `syslog`, set permission:

```bash
sudo chown syslog:syslog /var/spool/rsyslog
sudo chmod 770 /var/spool/rsyslog
```

If `rsyslog` runs as `root`, ownership change may not be required.

---

## 6. Create `/etc/rsyslog.d/49-devo.conf`

This file forwards Linux system logs to the Devo Relay.

```bash
sudo nano /etc/rsyslog.d/49-devo.conf
```

Add the following configuration:

```conf
template(
    name = "box-unix"
    type = "string"
    string = "<%PRI%>%timegenerated% %HOSTNAME% box.unix.%syslogtag% %msg%"
)

action(
    type="omfwd"
    template="box-unix"
    queue.type="LinkedList"
    queue.filename="boxq1"
    queue.saveonshutdown="on"
    action.resumeRetryCount="-1"
    Target="<DEVO_RELAY_IP>"
    Port="<DEVO_RELAY_PORT>"
    Protocol="tcp"
)
```

Replace these values:

| Placeholder | Description | Example |
|---|---|---|
| `<DEVO_RELAY_IP>` | Devo Relay IP address | `10.10.10.10` |
| `<DEVO_RELAY_PORT>` | Devo Relay listening port | `13011` |

Example with actual values:

```conf
template(
    name = "box-unix"
    type = "string"
    string = "<%PRI%>%timegenerated% %HOSTNAME% box.unix.%syslogtag% %msg%"
)

action(
    type="omfwd"
    template="box-unix"
    queue.type="LinkedList"
    queue.filename="boxq1"
    queue.saveonshutdown="on"
    action.resumeRetryCount="-1"
    Target="10.10.10.10"
    Port="13011"
    Protocol="tcp"
)
```

---

## 7. Why Use `49-devo.conf`

The `49-devo.conf` file forwards every message because it has no filter.

Because of this, it should be one of the last files processed in `/etc/rsyslog.d/`.

Check file order:

```bash
ls -1 /etc/rsyslog.d/
```

Example:

```text
00-devo.conf
40-iptables.conf
45-apache.conf
45-mongodb.conf
45-myapplogfile.conf
45-tomcat.conf
46-lt-monitor.conf
49-devo.conf
```

This helps prevent duplicated logs or unexpected forwarding behavior.

---

## 8. Validate rsyslog Configuration

Check rsyslog configuration syntax:

```bash
sudo rsyslogd -N1
```

Expected result should not show configuration errors.

---

## 9. Restart rsyslog

Restart service:

```bash
sudo systemctl restart rsyslog
```

Alternative command:

```bash
sudo /etc/init.d/rsyslog restart
```

Check status:

```bash
sudo systemctl status rsyslog
```

Check recent logs:

```bash
sudo journalctl -u rsyslog -n 100 --no-pager
```

---

## 10. Test Log Forwarding

Generate test messages:

```bash
logger "Hello from machine01"
logger "Hello from machine01"
logger "Hello from machine01"
logger "Hello from machine01"
logger "Hello from machine01"
```

Check local syslog:

### Ubuntu / Debian

```bash
sudo tail -f /var/log/syslog
```

### RHEL / CentOS / Rocky Linux

```bash
sudo tail -f /var/log/messages
```

---

## 11. Validate Logs Arrive at Devo Relay

On the Devo Relay server, run:

```bash
sudo tcpdump -i any host <LINUX_SERVER_IP> and port <DEVO_RELAY_PORT>
```

Example:

```bash
sudo tcpdump -i any host 10.10.20.15 and port 13011
```

If packets are visible, the Linux server is sending logs to the Devo Relay.

---

## 12. Validate in Devo

In Devo, open **Data Search** and query:

```sql
from box.unix
select *
limit 20
```

Search for the test message:

```sql
from box.unix
where message contains "Hello from machine01"
select *
limit 20
```

---

## 13. Troubleshooting

### rsyslog Cannot Start

Check service status:

```bash
sudo systemctl status rsyslog
```

Check logs:

```bash
sudo journalctl -u rsyslog -n 100 --no-pager
```

Validate syntax:

```bash
sudo rsyslogd -N1
```

Common causes:

| Issue | Cause |
|---|---|
| Syntax error | Wrong rsyslog configuration format |
| Permission denied | Wrong `/var/spool/rsyslog` ownership |
| Module load error | Missing or unsupported rsyslog module |

---

### Linux Server Cannot Connect to Relay

Test connection:

```bash
nc -vz <DEVO_RELAY_IP> <DEVO_RELAY_PORT>
```

Example:

```bash
nc -vz 10.10.10.10 13011
```

Check:

- Linux firewall
- Network firewall
- Routing
- Relay listener port
- Wrong relay IP
- Wrong relay port

---

### Relay Does Not Receive Logs

On the relay:

```bash
sudo tcpdump -i any host <LINUX_SERVER_IP> and port <DEVO_RELAY_PORT>
```

Check if relay is listening:

```bash
sudo ss -lntp | grep <DEVO_RELAY_PORT>
```

Example:

```bash
sudo ss -lntp | grep 13011
```


