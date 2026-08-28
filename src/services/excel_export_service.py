import io
from typing import List
import pandas as pd
from src.services.installment_report_service import InstallmentDetail


def export_installments_to_excel(
    installments: List[InstallmentDetail], lang: str = "fa"
) -> bytes:
    """تبدیل لیست اقساط به فایل اکسل در قالب خروجی بافر بایت"""
    data = []
    for item in installments:
        data.append(
            {
                "نام": item.first_name,
                "نام خانوادگی": item.last_name,
                "نوع بیمه": item.insurance_type,
                "شماره تلفن": item.phone,
                "شماره قسط": item.installment_number,
                "تاریخ سررسید": item.due_date_jalali,
                "مبلغ (ریال)": item.amount,
                "وضعیت": "پرداخت‌نشده" if item.status == "unpaid" else "پرداخت‌شده",
            }
        )

    df = pd.DataFrame(data)

    if installments:
        sheet_title = f"اقساط {installments[0].due_date_jalali}".replace("/", "-")
    else:
        sheet_title = "لیست اقساط"

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_title)

    return output.getvalue()