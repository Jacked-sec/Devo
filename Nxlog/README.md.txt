# Windows Log Collection to Devo Relay

## Overview

This document explains how to collect Windows Event Logs and forward them to a Devo Relay using NXLog.

## Architecture

```text
Windows Server / Endpoint
        ↓
      NXLog
        ↓
    Devo Relay
        ↓
     Devo Cloud
```

---

## Prerequisites

### Windows Side

- Windows Server or Windows Client
- NXLog Community Edition or NXLog Enterprise Edition
- Network connectivity from Windows host to Devo Relay
- Windows Firewall allows outbound traffic to Devo Relay

### Devo Relay Side

- Devo Relay installed and running
- Relay listener port is enabled
- Relay can send logs to Devo Cloud

Recommended outbound destinations from Devo Relay:

```text
collector-ap.devo.io:443
api-apac.devo.com:443
packages.devo.com:443
```

Recommended inbound ports on Devo Relay:

| Protocol | Port | Usage |
|---|---:|---|
| TCP | 13004 | Syslog TCP from Windows/NXLog |
| TCP/TLS | 6514 | Syslog TLS from Windows/NXLog |

---

## 1. Install NXLog on Windows

Download NXLog from the official website:

```text
https://nxlog.co/products/nxlog-community-edition/download
```

Install using the default options.

Default installation path:

```text
C:\Program Files\nxlog
```

Main configuration file:

```text
C:\Program Files\nxlog\conf\nxlog.conf
```

NXLog log file:

```text
C:\Program Files\nxlog\data\nxlog.log
```

---

## 2. NXLog Configuration - Syslog TCP

Replace `<DEVO_RELAY_IP>` with the Devo Relay IP address.

Example:

```conf
Panic Soft
#NoFreeOnExit TRUE
define ROOT     C:\Program Files\nxlog
define CERTDIR  %ROOT%\cert
define CONFDIR  %ROOT%\conf\nxlog.d
define LOGDIR   %ROOT%\data
include %CONFDIR%\\*.conf
define LOGFILE  %LOGDIR%\nxlog.log
LogFile %LOGFILE%
Moduledir %ROOT%\modules
CacheDir  %ROOT%\data
Pidfile   %ROOT%\data\nxlog.pid
SpoolDir  %ROOT%\data
<Extension _syslog>
    Module      xm_syslog
</Extension>
<Extension _charconv>
    Module      xm_charconv
    AutodetectCharsets iso8859-2, utf-8, utf-16, utf-32
</Extension>
<Extension _exec>
    Module      xm_exec
</Extension>
<Extension json>
    Module          xm_json
</Extension>

<Extension _fileop>
    Module      xm_fileop
    # Check the size of our log file hourly, rotate if larger than 5MB
<Schedule>
        Every   1 hour
        Exec    if (file_exists('%LOGFILE%') and \
                   (file_size('%LOGFILE%') >= 5M)) \
                    file_cycle('%LOGFILE%', 8);
</Schedule>
    # Rotate our log file every week on Sunday at midnight
<Schedule>
        When    @weekly
        Exec    if file_exists('%LOGFILE%') file_cycle('%LOGFILE%', 8);
</Schedule>
</Extension>
# Snare compatible example configuration
# Collecting event log
<Input in>
     Module      im_msvistalog
  ReadFromLast     True
  Query            <QueryList>\
<Query Id="0">\
<Select Path="Application">*</Select>\
<Select Path="System">*</Select>\
<Select Path="Security">*</Select>\
<Select Path="Windows PowerShell">*</Select>\
</Query>\
</QueryList>
</Input>
<Output devo_relay>
    Module      om_tcp
    Host        RelayIP
    Port        13004
    Exec        $Message = to_json(); $SourceName="box.win_nxlog."+lc($Channel); delete($ProcessID); to_syslog_bsd();
</Output>
<Route 1>
    Path        in => devo_relay
</Route>
```

---

## 3. NXLog Configuration - Syslog TLS

TLS is recommended for production environments.

Certificate path example:

```text
C:\Program Files\nxlog\cert
```

Example configuration:

```conf
define ROOT C:\Program Files\nxlog

Moduledir %ROOT%\modules
CacheDir %ROOT%\data
Pidfile %ROOT%\data\nxlog.pid
SpoolDir %ROOT%\data
LogFile %ROOT%\data\nxlog.log

<Extension _syslog>
    Module xm_syslog
</Extension>

<Input windows_eventlog>
    Module im_msvistalog

    Query <QueryList>\
        <Query Id="0">\
            <Select Path="Security">*</Select>\
            <Select Path="System">*</Select>\
            <Select Path="Application">*</Select>\
        </Query>\
    </QueryList>
</Input>

<Output devo_relay_tls>
    Module om_ssl
    Host <DEVO_RELAY_IP>
    Port 6514

    CAFile   %ROOT%\cert\ca.crt
    CertFile %ROOT%\cert\client.crt
    CertKeyFile %ROOT%\cert\client.key

    Exec to_syslog_bsd();
</Output>

<Route windows_to_devo>
    Path windows_eventlog => devo_relay_tls
</Route>
```

---

## 4. Collect Additional Windows Logs

### Add Sysmon

Add this line inside the `Query` section:

```conf
<Select Path="Microsoft-Windows-Sysmon/Operational">*</Select>
```

Example:

```conf
#define ROOT C:\Program Files\nxlog
define ROOT C:\Program Files\nxlog
define LOGDIR %ROOT%\data
define LOGFILE %LOGDIR%\nxlog.log
LogFile %LOGFILE%
Moduledir %ROOT%\modules
CacheDir %ROOT%\data
Pidfile %ROOT%\data\nxlog.pid
SpoolDir %ROOT%\data
<Extension json>
Module xm_json
</Extension>
#DateFormat YYYY-MM-DDThh:mm:ss.sUTC - Not available in Community version
#GenerateDateInUTC TRUE
<Extension syslog>
Module xm_syslog
</Extension>
<Input in>
Module im_msvistalog
ReadFromLast True
<QueryXML>
<QueryList>
<Query Id="0">
<Select Path="Application">*</Select>
<Select Path="System">*</Select>
<Select Path="Security">*</Select>
<Select Path="Windows PowerShell">*</Select>
<Select Path="Microsoft-Windows-Sysmon/Operational">*</Select>
</Query>
</QueryList>
</QueryXML>
Exec $UnixTime = integer($EventTime)/1000;
</Input>
<Output devo_relay>
Module om_tcp
Host <RelayIP>
Port 13000
Exec        $Message = to_json(); \
                if ($Channel == "Microsoft-Windows-Sysmon/Operational") \
                  $SourceName = "box.win_nxlog.sysmon"; \
                else \
                  $SourceName = "box.win_nxlog." + lc($Channel); \
                   delete($ProcessID); to_syslog_bsd();
#Exec
</Output>
<Output file>
Module om_file
File 'C:\nxlog_events.log'
Exec $Message = to_json(); $SourceName="box.win_nxlog."+lc($Channel); delete($ProcessID); to_syslog_bsd();
</Output>
<Route 1>
Path in => devo_relay
#Path in => file
</Route>
```

### Add PowerShell Logs

```conf
<Select Path="Windows PowerShell">*</Select>
<Select Path="Microsoft-Windows-PowerShell/Operational">*</Select>
```

### Add Windows Defender Logs

```conf
<Select Path="Microsoft-Windows-Windows Defender/Operational">*</Select>
```

---

## 5. Recommended Windows Event Logs

| Log Source | Priority | Description |
|---|---|---|
| Security | High | Authentication, privilege use, account activity |
| System | High | Service, driver, system-level events |
| Application | Medium | Application errors and application activity |
| Sysmon | Critical | Process, network, registry, file activity |
| PowerShell | High | Script execution and command activity |
| Windows Defender | High | Malware detection and protection events |

---

## 6. Recommended Security Event IDs

| Event ID | Description |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4634 | Logoff |
| 4648 | Logon using explicit credentials |
| 4672 | Special privileges assigned |
| 4688 | Process creation |
| 4697 | Service installed |
| 4720 | User account created |
| 4722 | User account enabled |
| 4723 | Password change attempt |
| 4728 | User added to security-enabled global group |
| 4732 | User added to security-enabled local group |
| 4738 | User account changed |
| 4740 | User account locked out |
| 4768 | Kerberos TGT requested |
| 4771 | Kerberos pre-authentication failed |
| 4776 | NTLM authentication |
| 5140 | Network share accessed |
| 5142 | Network share created |
| 5145 | Detailed file share access |

---

## 7. Restart NXLog Service

Run Command Prompt as Administrator:

```cmd
net stop nxlog
net start nxlog
```

Or use PowerShell:

```powershell
Restart-Service nxlog
```

Check service status:

```powershell
Get-Service nxlog
```

---

## 8. Validate Connectivity from Windows to Devo Relay

Test TCP connection:

```powershell
Test-NetConnection <DEVO_RELAY_IP> -Port 13004
```

For TLS:

```powershell
Test-NetConnection <DEVO_RELAY_IP> -Port 6514
```

Expected result:

```text
TcpTestSucceeded : True
```

---

## 9. Validate NXLog Status

Check NXLog log file:

```text
C:\Program Files\nxlog\data\nxlog.log
```

Common healthy condition:

```text
no connection error
no module error
no certificate error
```

Common errors:

| Error | Possible Cause |
|---|---|
| connection refused | Relay port is not listening |
| connection timed out | Firewall or routing issue |
| certificate verify failed | TLS certificate problem |
| couldn't parse config | NXLog configuration syntax error |

---

## 10. Validate Logs on Devo Relay

Run this command on Devo Relay:

```bash
sudo tcpdump -i any port 13004
```

For TLS:

```bash
sudo tcpdump -i any port 6514
```

Check listening port:

```bash
sudo ss -lntp | grep -E '13004|6514'
```

Check relay service:

```bash
sudo systemctl status devo-relay
```

---

## 11. Validate Relay Outbound Connectivity to Devo Cloud

Test DNS:

```bash
nslookup collector-ap.devo.io
nslookup api-apac.devo.com
```

Test HTTPS connection:

```bash
curl -v https://collector-ap.devo.io
curl -v https://api-apac.devo.com
```

Expected result:

```text
TLS handshake completed
HTTP response received
```

---

## 12. Verify Logs in Devo

Example Devo queries:

```sql
from box.all.win
select *
limit 10
```

or:

```sql
from box.win_nxlog
select *
limit 10
```

Check by hostname:

```sql
from box.all.win
where source_hostname = "<HOSTNAME>"
select *
limit 20
```

Check by Event ID:

```sql
from box.all.win
where event_id = 4625
select eventdate, source_hostname, account, source_ip, event_id
limit 20
```

---

## 13. Troubleshooting

### Case 1: Windows Cannot Connect to Relay

Check from Windows:

```powershell
Test-NetConnection <DEVO_RELAY_IP> -Port 13010
```

Check Windows Firewall outbound rule.

Check network firewall between Windows and Relay.

Check Devo Relay is listening:

```bash
sudo ss -lntp | grep 13004
```

---

### Case 2: NXLog Service Cannot Start

Check config syntax and logs:

```text
C:\Program Files\nxlog\data\nxlog.log
```

Restart service after fixing the configuration:

```powershell
Restart-Service nxlog
```

---

