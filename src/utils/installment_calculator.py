from typing import List


def split_installment_amount(total_amount: int, down_payment: int, count: int) -> List[int]:

    rem_amount = total_amount - down_payment
    base_amount = rem_amount // count
    remainder = rem_amount % count

    amounts = [base_amount] * count
    amounts[-1] += remainder 
    return amounts