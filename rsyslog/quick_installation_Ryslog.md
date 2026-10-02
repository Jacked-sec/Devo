#quick installation
1.
```bash
sudo cp /etc/rsyslog.conf /etc/rsyslog.conf.bak
```
2.
```bash
sudo tee -a /etc/rsyslog.conf > /dev/null <<'EOF'

# ==============================
# Forward logs to Devo Relay
# ==============================

template(
    name="box-unix"
    type="string"
    string="<%PRI%>%timegenerated% %HOSTNAME% box.unix.%syslogtag% %msg%"
)

action(
    type="omfwd"
    template="box-unix"
    queue.type="LinkedList"
    queue.filename="boxq1"
    queue.saveonshutdown="on"
    action.resumeRetryCount="-1"
    Target="<IPRELAY>"
    Port="<PORT>"
    Protocol="tcp"
)
EOF
```
3.
```bash
sudo systemctl restart rsyslog
sudo systemctl status rsyslog
```
