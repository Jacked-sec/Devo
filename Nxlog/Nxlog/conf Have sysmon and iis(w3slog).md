```conf
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

<Extension syslog>
    Module xm_syslog
</Extension>

# --- Input: Windows Event Log ---
<Input win_eventlog>
    Module im_msvistalog
    ReadFromLast TRUE
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

# --- Input: IIS Log (raw) ---
<Input iis_access>
    Module      im_file
    File        'C:\inetpub\logs\LogFiles\W3SVC*\u_ex*.log'
<Exec>
        if $raw_event =~ /^#/ drop();
</Exec>
</Input>

# --- Output: Devo TCP Relay Output win_eventlog ---
<Output devo_relay>
    Module om_tcp
    Host <relayip>
    Port 13005
    Exec \
        if defined($Channel) and $Channel == "Microsoft-Windows-Sysmon/Operational" { \
            $SourceName = "box.win_nxlog.sysmon"; \
        } \
        else if defined($Channel) { \
            $SourceName = "box.win_nxlog." + lc($Channel); \
        } \
        $Message = to_json(); \
        delete($ProcessID); \
        to_syslog_bsd();
</Output>

<Output devo_relay_iis>
    Module om_tcp
    Host <relayip>
    Port 13006
    Exec to_syslog_bsd();  # Or to_syslog_snare() if Devo requires
</Output>

# --- Output (debug file) ---
<Output file>
    Module om_file
    File 'C:\\nxlog_events.log'
    Exec $Message = to_json(); delete($ProcessID); to_syslog_bsd();
</Output>

# --- Routes ---
<Route route_eventlog>
    Path win_eventlog => devo_relay
</Route>

<Route route_iis>
    Path iis_access => devo_relay_iis
</Route>
```
