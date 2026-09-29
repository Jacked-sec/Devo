# Ubuntu → Devo SIEM: Log Forwarding Cheat Sheet

คู่มือคำสั่งสำหรับตั้งค่าและตรวจสอบ Ubuntu → rsyslog → Devo Relay → Devo SIEM

## ก่อนเริ่ม

- แทน `<DEVO_RELAY_IP>` และ `<PORT>` ด้วย IP และพอร์ตรับ Log ที่ตั้งไว้บน Relay จริง ไม่ใช่ URL ของหน้าเว็บ Devo
- พอร์ตและโปรโตคอลต้องตรงกับ Listener/Rule ของ Relay รวมถึงการกำหนด Devo tag และตารางปลายทาง
- ตัวอย่างนี้ใช้ **TCP แบบไม่เข้ารหัสไปยัง Relay** หากปลายทางกำหนด TLS หรือส่งตรงเข้า Devo Cloud ต้องใช้การตั้งค่า TLS/ใบรับรองตามเอกสารของปลายทาง
- คำสั่งที่มี `<...>` เป็นแม่แบบ ต้องแทนค่าก่อนรัน; คำสั่ง `-f` และ `tcpdump` หยุดด้วย `Ctrl+C`
- คำสั่งติดตั้ง แก้ Config และ Restart เปลี่ยนแปลงระบบ ส่วนคำสั่งตรวจสอบใช้เพื่ออ่านสถานะ

## ตารางคำสั่งทั้งหมด

| หมวด | Command | ใช้ทำอะไร / สิ่งที่ควรดู |
|---|---|---|
| ข้อมูลเครื่อง | `hostname` | ดู Hostname เพื่อใช้ค้นหาใน Devo |
| ข้อมูลเครื่อง | `hostname -I` | ดู IP ของเครื่อง |
| ข้อมูลเครื่อง | `cat /etc/os-release` | ดู Ubuntu Version |
| เวลา | `timedatectl status` | ดูเวลา Timezone และสถานะการ Sync เวลา |
| Network | `ip a` | ดู Interface และ IP |
| Network | `ip route get <DEVO_RELAY_IP>` | ดู Route และ Source IP ที่ใช้ไป Relay |
| ติดตั้ง | `sudo apt update && sudo apt install rsyslog netcat-openbsd tcpdump` | ติดตั้งเมื่อยังไม่มีเครื่องมือเหล่านี้ |
| rsyslog | `systemctl status rsyslog --no-pager` | ดูสถานะ Service และข้อความล่าสุด |
| rsyslog | `systemctl is-active rsyslog` | ตรวจว่า Service ทำงานอยู่หรือไม่ |
| rsyslog | `systemctl is-enabled rsyslog` | ตรวจว่าเปิดทำงานตอน Boot หรือไม่ |
| rsyslog | `rsyslogd -v` | ดู Version ของ rsyslog |
| rsyslog | `sudo systemctl enable --now rsyslog` | เริ่ม Service และเปิดให้ทำงานตอน Boot เมื่อจำเป็น |
| Config | `sudo cat /etc/rsyslog.conf` | ดู Config หลักและ Include ของไฟล์ย่อย |
| Config | `ls -l /etc/rsyslog.d/` | ดูไฟล์ Config เพิ่มเติม |
| Config | `sudo cat /etc/rsyslog.d/<file>.conf` | ดู Config ที่ระบุ |
| Config | `sudo grep -R -n . /etc/rsyslog.d/` | ดูบรรทัดที่ไม่ว่างของ Config ย่อยทั้งหมด |
| Config | `sudo grep -Rni 'target[[:space:]]*=' /etc/rsyslog.conf /etc/rsyslog.d/` | หา Target ใน Config แบบ action |
| Config | `sudo grep -Rn '@@' /etc/rsyslog.conf /etc/rsyslog.d/` | หา TCP Forwarding แบบเก่า |
| Config | `sudo grep -Rn '@' /etc/rsyslog.conf /etc/rsyslog.d/` | หา Forwarding แบบเก่าทั้ง TCP และ UDP; อาจพบ Comment ด้วย |
| Config | `sudo nano /etc/rsyslog.d/60-devo-forward.conf` | สร้างหรือแก้ Config Forwarding |
| Validate | `sudo rsyslogd -N1` | ตรวจ Config ก่อน Restart; ต้องไม่มี Error |
| Restart | `sudo systemctl restart rsyslog` | โหลด Config ใหม่โดย Restart Service |
| Log/Error | `sudo journalctl -u rsyslog -n 100 --no-pager` | ดู Log/Error ล่าสุดของ Service |
| Log/Error | `sudo journalctl -u rsyslog --since '15 minutes ago' --no-pager` | ดู Error ช่วงที่กำลังตรวจสอบ |
| Log/Error | `sudo journalctl -u rsyslog -f` | ติดตาม Log ของ Service แบบ Real-time |
| Connectivity | `ping -c 4 <DEVO_RELAY_IP>` | ตรวจ ICMP; ไม่ตอบไม่ได้แปลว่า TCP ใช้งานไม่ได้ |
| Connectivity | `nc -vz -w 3 <DEVO_RELAY_IP> <PORT>` | ทดสอบการเชื่อมต่อ TCP; สำเร็จยังไม่ยืนยันว่า Log เข้า Devo |
| Connection | `sudo ss -antp` | ดู TCP Connection และ Process ที่เกี่ยวข้อง |
| Connection | `sudo ss -antp \| grep -F '<DEVO_RELAY_IP>:<PORT>'` | กรอง Connection ไป Relay สำหรับ IPv4; ดู ESTAB/SYN-SENT |
| Connection | `sudo ss -antp \| grep ':<PORT>'` | กรอง Connection ตามพอร์ตอย่างคร่าว ๆ |
| Firewall | `sudo ufw status verbose` | ดูสถานะ UFW; ไม่ครอบคลุม Firewall ภายนอกเครื่อง |
| Test Log | `logger -p user.notice -t devo_test "Test log from $(hostname) at $(date -Is)"` | สร้าง Test Log ผ่าน Local Syslog |
| Test Log | `sudo journalctl -t devo_test --since '10 minutes ago' --no-pager` | หา Test Log ใน Journal |
| Test Log | `sudo grep -F devo_test /var/log/syslog` | หา Test Log ในไฟล์ ถ้าเครื่องกำหนดให้เขียนไฟล์นี้ |
| Packet | `sudo tcpdump -ni any -nn 'host <DEVO_RELAY_IP>'` | ดู Traffic ระหว่างเครื่องกับ Relay |
| Packet | `sudo tcpdump -ni any -nn 'host <DEVO_RELAY_IP> and tcp port <PORT>'` | ดู Traffic เฉพาะ TCP Port ปลายทาง |
| Packet | `sudo tcpdump -ni any -nn -A -s 0 -c 20 'host <DEVO_RELAY_IP> and tcp port <PORT>'` | ดู Payload ไม่เกิน 20 Packet; อ่านได้เมื่อไม่เข้ารหัสและอาจมีข้อมูลใน Log |
| Storage | `df -h / /var/log` | ดูพื้นที่ดิสก์เมื่อเขียน Log ไม่ได้ |

> การพบ Test Log ใน Journal หรือ `/var/log/syslog` ยืนยันเฉพาะการรับ/เก็บในเครื่อง ต้องค้นหาข้อความเดียวกันใน Devo เพื่อยืนยันครบเส้นทาง

## Core commands: ชุดคำสั่งหลัก

| ลำดับ | Command | จุดประสงค์ |
|---|---|---|
| 1 | `systemctl status rsyslog --no-pager` | Service ต้องทำงาน |
| 2 | `sudo cat /etc/rsyslog.d/60-devo-forward.conf` | ตรวจ IP, Port และ Protocol |
| 3 | `sudo rsyslogd -N1` | ตรวจ Config; ถ้ามี Error ให้แก้ก่อน |
| 4 | `nc -vz -w 3 <DEVO_RELAY_IP> <PORT>` | ตรวจ TCP ไป Relay |
| 5 | `sudo systemctl restart rsyslog` | ทำเมื่อแก้ Config และ Validate ผ่านแล้ว |
| 6 | `logger -p user.notice -t devo_test "Test log from $(hostname) at $(date -Is)"` | สร้างข้อความทดสอบ |
| 7 | `sudo journalctl -u rsyslog -n 100 --no-pager` | ตรวจ Error หลังส่ง |
| 8 | `sudo tcpdump -ni any -nn 'host <DEVO_RELAY_IP> and tcp port <PORT>'` | ตรวจ Traffic เมื่อยังไม่เห็น Log |

## ตัวอย่าง rsyslog TCP forwarding

สร้างหรือแก้ไฟล์:

```bash
sudo nano /etc/rsyslog.d/60-devo-forward.conf
```

วาง Config นี้แล้วเปลี่ยน IP และ Port ให้ตรงกับ Relay:

```conf
# Example only: replace the destination with your Relay listener.
*.* action(
    type="omfwd"
    target="192.0.2.10"
    port="13006"
    protocol="tcp"
    action.resumeRetryCount="-1"
    queue.type="LinkedList"
    queue.size="10000"
)
```

- `192.0.2.10` เป็น IP สำหรับเอกสาร และ `13006` เป็นเพียงพอร์ตตัวอย่าง ไม่ใช่พอร์ตมาตรฐานที่ใช้ได้กับทุก Devo Relay
- `*.*` เลือกทุก Facility/Severity ที่มาถึงกฎนี้ ไม่ได้อ่านไฟล์ทุกไฟล์ใน `/var/log` โดยอัตโนมัติ; Log จากไฟล์แอปอาจต้องตั้ง Input เช่น `imfile`
- Queue นี้อยู่ในหน่วยความจำ แยกการส่งออกจากการประมวลผลหลัก และลองเชื่อมต่อใหม่ต่อเนื่องเมื่อ Action ล้มเหลว แต่ไม่รับประกันว่า Log จะไม่สูญหายเมื่อ Queue เต็มหรือ Process หยุด
- ตรวจ Filter, Ruleset และ `stop` ใน Config ก่อนหน้า เพราะอาจทำให้ข้อความมาไม่ถึงกฎนี้ รวมถึงตรวจว่าไม่มี Forwarding ซ้ำ
- รูปแบบข้อความและ TCP framing ต้องตรงกับที่ Relay รับได้ ตัวอย่างนี้ใช้ค่าเริ่มต้นของ rsyslog จึงต้องตรวจความเข้ากันได้กับ Listener จริง

ตรวจ Config และ Restart เฉพาะเมื่อผ่าน:

```bash
sudo rsyslogd -N1 && sudo systemctl restart rsyslog
systemctl is-active rsyslog
sudo journalctl -u rsyslog -n 50 --no-pager
```

ส่ง Test Log แล้วค้นหา `devo_test` หรือข้อความทดสอบในตาราง Devo ที่ Relay Rule กำหนด:

```bash
logger -p user.notice -t devo_test "Test log from $(hostname) at $(date -Is)"
```

### Syntax แบบเก่า: สำหรับอ่าน Config เดิม

```conf
# TCP
*.* @@192.0.2.10:13006

# UDP
*.* @192.0.2.10:13006
```

เลือกเฉพาะรูปแบบและโปรโตคอลที่ใช้จริง ห้ามเพิ่มทั้งสองบรรทัดหรือเพิ่มซ้ำกับ action ตัวอย่าง เพราะอาจส่ง Log ซ้ำ; `@@` เพียงอย่างเดียวไม่ได้เปิด TLS

## Troubleshooting flow

```text
ไม่เห็น Log ใน Devo
  → rsyslog ทำงานหรือไม่?
  → Config ผ่านและ Target/Port/Protocol ถูกหรือไม่?
  → เชื่อมต่อ TCP ไป Relay ได้หรือไม่?
  → สร้าง Test Log และพบในเครื่องหรือไม่?
  → มี Traffic ออกจากเครื่องไป Relay หรือไม่?
  → Relay รับ Log และจับคู่ Rule/Tag ถูกหรือไม่?
  → Relay ส่งต่อเข้า Devo ได้หรือไม่?
  → ค้นหาถูกตาราง ช่วงเวลา และข้อความหรือไม่?
```

| ขั้นตอน | วิธีตรวจ | หากไม่ผ่าน / ขั้นตอนต่อไป |
|---|---|---|
| 1. Service | `systemctl status rsyslog --no-pager` และ `sudo journalctl -u rsyslog -n 100 --no-pager` | ตรวจสาเหตุ เช่น Config ผิด สิทธิ์ไฟล์ หรือดิสก์เต็ม แล้วเริ่ม Service หลังแก้ |
| 2. Config | `sudo rsyslogd -N1` และอ่าน Forwarding Config | แก้ Error ตรวจ Include, Filter, Ruleset, `stop`, IP, Port และ TCP/TLS ให้ตรงกัน; Validate ไม่ได้ทดสอบเครือข่าย |
| 3. Network | `ip route get <DEVO_RELAY_IP>` และ `nc -vz -w 3 <DEVO_RELAY_IP> <PORT>` | Timeout: ตรวจ Route/Firewall/ปลายทาง; Refused: ตรวจ Listener หรือการ Reject ที่ปลายทาง |
| 4. Local event | ส่ง `logger` แล้วค้นด้วย `journalctl -t devo_test` หรือใน `/var/log/syslog` | ตรวจ Local Logging/Input และ Filter; ไม่มีไฟล์ syslog อาจเป็นเพราะเครื่องไม่ได้ตั้งให้เขียนไฟล์นี้ |
| 5. Outbound traffic | เปิด `tcpdump` ตามตาราง แล้วส่ง Test Log อีกครั้ง | ไม่มี Traffic: ตรวจ Action/Filter และ Service Error; มี SYN ซ้ำ: ตรวจการตอบกลับจากปลายทาง; มี Traffic ยังไม่ยืนยันการจัดเก็บใน Devo |
| 6. Relay input | บน Relay ให้ผู้ดูแลตรวจ Listener, Packet ขาเข้า และ Rule ที่ผูกกับ Port/Source | ตรวจ Protocol, รูปแบบข้อความ, framing และ Devo tag/table ที่ Rule กำหนด |
| 7. Relay output | ตรวจสถานะและ Error ของ Relay รวมถึงการเชื่อมต่อออกไป Devo | ตรวจ Queue ค้าง การเชื่อมต่อปลายทาง และใบรับรอง/TLS ตามการติดตั้งจริง |
| 8. Devo search | เลือกตารางตาม Tag/Rule แล้วค้นข้อความ Test Log, Hostname และเวลาที่ส่ง | ขยายช่วงเวลา ตรวจ Timezone, เวลาเครื่อง, สิทธิ์เข้าถึงตาราง และความล่าช้าในการรับข้อมูล |

**เกณฑ์สำเร็จ:** พบข้อความทดสอบเดียวกันในตาราง Devo ที่คาดไว้ และตรวจว่า Hostname/เวลา/การแยกฟิลด์ถูกต้องตามรูปแบบ Log ที่ใช้งาน

## เอกสารอ้างอิง

- [rsyslog: Forwarding Logs](https://docs.rsyslog.com/doc/getting_started/forwarding_logs.html)
- [rsyslog: omfwd output module](https://docs.rsyslog.com/doc/configuration/modules/omfwd.html)
- [rsyslog: Understanding Queues](https://docs.rsyslog.com/doc/concepts/queues.html)
- [Devo: Planning Devo Relay deployment](https://docs.devo.com/space/latest/96469035)

เอกสารนี้เป็น Cheat Sheet สำหรับปรับใช้ตามระบบจริง ไม่ผูกกับ IP, Port หรือ Tag ขององค์กรใด
