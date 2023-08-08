import threading
from django.db import connection
from .models import Merchant


def race_condition_check():
    def thread_task(name):
        for i in range(5):
            merchant = Merchant.objects.first()
            merchant.add_credit(1)
            print(
                "The merchant's credit as incremented by thread_id %d is: " % (name),
                merchant.credit,
            )

    def main():
        merchant = Merchant.objects.first()
        merchant.credit = 0
        merchant.save()

        t1 = threading.Thread(target=thread_task, args=(1,))
        t2 = threading.Thread(target=thread_task, args=(2,))

        t1.start()
        print(" ---Thread 1 Started----")
        t2.start()
        print(" ---Thread 2 Started----")
        t1.join()  # To tell one thread to wait for another thread to finish
        print(" ---Thread 1 Joined----")
        t2.join()
        print(" ---Thread 2 Joined----")

    for i in range(3):
        print("---Doing the round %d: " % (i))
        main()
