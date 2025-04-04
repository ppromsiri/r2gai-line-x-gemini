import functions_framework
from flask import jsonify


def calculate_max_loan(monthly_income, existing_debt, loan_term_years):
    """
    คำนวณวงเงินกู้สูงสุดโดยอิงจากรายได้ต่อเดือน และภาระผ่อนสูงสุดไม่เกิน 65% และหักลบภาระหนี้ที่มีอยู่
    """
    max_payment_ratio = 0.65  # อัตราภาระผ่อนสูงสุด 65%
    interest_rate = 6.5  # อัตราดอกเบี้ยสมมุติ (ร้อยละต่อปี)
    max_total_payment = monthly_income * max_payment_ratio

    # หักลบภาระหนี้รายเดือนที่มีอยู่
    available_payment = max_total_payment - existing_debt
    if available_payment <= 0:
        return 0, 0, "You can't afford any additional installments"

    loan_term_months = loan_term_years * 12
    monthly_interest_rate = interest_rate / 12 / 100

    # คำนวณวงเงินกู้สูงสุดด้วยสูตรเงินงวดผ่อน (PMT)
    loan_amount = available_payment * (
        (1 - (1 + monthly_interest_rate) ** -loan_term_months) / monthly_interest_rate
    )

    return (
        round(loan_amount),
        round(available_payment),
        "Loan amount calculated successfully",
    )


@functions_framework.http
def handle_http_request(request):

    request_json = request.get_json(silent=True)
    print("Request: " + str(request_json))

    # Extract data from JSON body
    monthly_income = int(request_json.get("monthly_income", 0))
    existing_debt = request_json.get("existing_debt", 0)
    loan_term_years = request_json.get("use_spouse_allowance", 0)

    max_loan, monthly_payment, message = calculate_max_loan(
        monthly_income, existing_debt, loan_term_years
    )
    return jsonify(
        {
            "max_loan": f"{max_loan:.2f}",
            "monthly_payment": f"{monthly_payment:.2f}",
            "message": message,
        }
    )


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    monthly_income = 100000  # รายได้ต่อเดือน
    existing_debt = 600000  # ภาระหนี้รายเดือน
    loan_term_years = 30

    max_loan, monthly_payment = calculate_max_loan(
        monthly_income, existing_debt, loan_term_years
    )

    print(f"วงเงินกู้สูงสุด: {max_loan:,.0f} บาท")
    print(f"ยอดผ่อนต่อเดือน: {monthly_payment:,.0f} บาท")
