import threading
from multiprocessing import Process

from django.db import connection
from .models import Merchant


def race_condition_check_threaded():
    def thread_task(name):
        for i in range(5):
            merchant = Merchant.objects.first()
            print(
                "The merchant's credit as seen by thread_id %d is: " % (name),
                merchant.credit,
            )
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
        print("  *Thread 1 Started* ")
        t2.start()
        print("  *Thread 2 Started* ")
        t1.join()  # To tell one thread to wait for another thread to finish
        print("  *Thread 1 Joined*  ")
        t2.join()
        print("  *Thread 2 Joined*  ")

    for i in range(1):
        print("--->>> Round %d: " % (i))
        main()
    connection.close()


def race_condition_check_multiprocess():
    def process_task(name=0):
        for i in range(5):
            merchant = Merchant.objects.first()
            print(
                "The merchant's credit as seen by process_id %d is: " % (name),
                merchant.credit,
            )
            merchant.add_credit(1)
            print(
                "The merchant's credit as incremented by process_id %d is: " % (name),
                merchant.credit,
            )

    def main():
        merchant = Merchant.objects.first()
        merchant.credit = 0
        merchant.save()
        connection.close()  # due to an error

        names = [1, 2]
        procs = []

        # instantiating process with arguments
        for name in names:
            print("  *Process 1 Started* ")
            proc = Process(target=process_task, args=(name,))
            procs.append(proc)
            proc.start()

        # complete the processes
        for proc in procs:
            proc.join()

    for i in range(1):
        print("--->>> Round %d: " % (i))
        main()
    connection.close()
