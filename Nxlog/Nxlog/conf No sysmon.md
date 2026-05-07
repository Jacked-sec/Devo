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
