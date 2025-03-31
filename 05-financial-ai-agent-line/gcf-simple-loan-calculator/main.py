def calculate_max_loan(income, interest_rate, loan_term_years):
    """
    คำนวณวงเงินกู้สูงสุดโดยอิงจากรายได้ต่อเดือน และภาระผ่อนสูงสุดไม่เกิน 65%
    """
    max_payment_ratio=0.65  # อัตราภาระผ่อนสูงสุด 65%
    monthly_income = income
    max_monthly_payment = monthly_income * max_payment_ratio
    loan_term_months = loan_term_years * 12
    monthly_interest_rate = interest_rate / 12 / 100

    # คำนวณวงเงินกู้สูงสุดด้วยสูตรเงินงวดผ่อน (PMT)
    # P = PMT * ((1 - (1 + r)^-n) / r)
    loan_amount = max_monthly_payment * ((1 - (1 + monthly_interest_rate) ** -loan_term_months) / monthly_interest_rate)

    return round(loan_amount), round(max_monthly_payment)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    income = 100000  # รายได้ต่อเดือน
    interest_rate = 6.5  # อัตราดอกเบี้ยสมมุติ (ร้อยละต่อปี)
    loan_term_years = 30

    max_loan, monthly_payment = calculate_max_loan(income, interest_rate, loan_term_years)

    print(f"วงเงินกู้สูงสุด: {max_loan:,.0f} บาท")
    print(f"ยอดผ่อนต่อเดือน: {monthly_payment:,.0f} บาท")
