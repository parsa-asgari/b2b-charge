import threading
from django.db import connection
from .models import Merchant


def task():
    merchant = Merchant.objects.first()
    merchant.add_credit(1)
    print(
        "The merchant's credit as seen by thread_id %d is: " % (threading.get_ident()),
        merchant.credit,
    )


def thread_task():
    for i in range(5):
        task()


def main():
    merchant = Merchant.objects.first()
    merchant.credit = 0
    merchant.save()

    t1 = threading.Thread(target=thread_task)
    t2 = threading.Thread(target=thread_task)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


for i in range(2):
    main()
