# ฟังก์ชันสำหรับคำนวณค่าใช้จ่าย
def calculate_badminton_cost(hourly_rate, hours, courts, shuttle_price, shuttle_count, people):
    # คำนวณค่าสนาม
    court_cost = hourly_rate * hours * courts
    # คำนวณค่าลูกแบด
    shuttle_cost = shuttle_price * shuttle_count
    # รวมค่าใช้จ่ายทั้งหมด
    total_cost = court_cost + shuttle_cost
    # คำนวณค่าใช้จ่ายต่อคน
    cost_per_person = total_cost / people
    return total_cost, cost_per_person

# รับข้อมูลจากผู้ใช้
hourly_rate = 170  # ค่าสนามต่อชั่วโมง
hours = 2          # จำนวนชั่วโมงที่จอง
courts = 1         # จำนวนสนามที่จอง
shuttle_price = 46 # ราคาลูกแบดต่อลูก
shuttle_count = 4  # จำนวนลูกแบด
people = 6         # จำนวนคน

# คำนวณค่าใช้จ่าย
total_cost, cost_per_person = calculate_badminton_cost(hourly_rate, hours, courts, shuttle_price, shuttle_count, people)

# แสดงผลลัพธ์
print(f"ค่าใช้จ่ายรวม: {total_cost:.2f} บาท")
print(f"ค่าใช้จ่ายต่อคน: {cost_per_person:.2f} บาท")
