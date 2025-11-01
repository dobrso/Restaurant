import threading
import queue
import time
import random
import json
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    COOKING = "cooking"
    READY = "ready"
    COMPLETED = "completed"

class OrderSystem:
    def __init__(self):
        self.kitchen_ready = threading.Event()

        self.stove_condition = threading.Condition()
        self.available_stoves = 2

        self.order_queue = queue.Queue(maxsize=10)

        self.stats = {
            "total_orders": 0,
            "completed_orders": 0,
            "failed_orders": 0,
            "cooking_time_total": 0
        }
        self.stats_lock = threading.Lock()

        self.system_running = False

        self.producers = []
        self.consumers = []
        self.monitor_thread = None

    def kitchen_preparation(self):
        print("ПОВАР: Начинаю подготовку кухни...")

        tasks = [
            "Проверяю оборудование",
            "Настраиваю температуру плит",
            "Подготавливаю ингредиенты",
            "Запускаю вытяжку"
        ]

        for task in tasks:
            print(f"Повар: {task}")
            time.sleep(1)

        print("Повар: ОТКРЫВАЕМСЯ!!!")
        self.kitchen_ready.set()

    def order_producer(self, producer_id):

        menu_items = [
            "Паста",
            "Борщ",
            "Пельмеши",
            "Блины",
            "Рис с овощами"
        ]

        self.kitchen_ready.wait()
        while self.system_running:
            order = {
                "order_id": random.randint(1000, 9999),
                "customer_id": random.randint(1, 100),
                "dish": random.choice(menu_items),
                "complexity": random.randint(1, 5),
                "status": OrderStatus.PENDING.value,
                "created_time": datetime.now(),
                "producer_id": producer_id
            }

            if self.order_queue.full():
                with self.stats_lock:
                    self.stats["failed_orders"] += 1

                print(f"Официант {producer_id}: не смог принять заказ, очередь переполнена")

                time.sleep(random.uniform(0.5, 2))
                continue

            self.order_queue.put(order)

            with self.stats_lock:
                self.stats["total_orders"] += 1
            
            print(f"Официант {producer_id}: принял заказ #{order["order_id"]} {order["dish"]}")        

            time.sleep(random.uniform(0.5, 2))

    def chef_consumer(self, chef_id):
        self.kitchen_ready.wait()
        while self.system_running:
            order = self.order_queue.get()

            with self.stove_condition:
                if self.available_stoves == 0:
                    print(f"Повар {chef_id}: ждет свободную конфорку")      
                    self.stove_condition.wait()

                self.available_stoves -= 1
                print(f"Повар {chef_id}: занял свободную конфорку")
                print(f"Повар {chef_id}: начал готовить заказ #{order["order_id"]}")

                order["status"] = OrderStatus.COOKING.value

            cook_time = order["complexity"] * 0.5
            time.sleep(cook_time)

            order["status"] = OrderStatus.COMPLETED.value

            with self.stove_condition:
                self.available_stoves += 1
                print(f"Повар {chef_id}: освободил конфорку")
                self.stove_condition.notify()

            with self.stats_lock:
                self.stats["completed_orders"] += 1
                self.stats["cooking_time_total"] += cook_time

            print(f"Повар {chef_id}: приготовил заказ #{order["order_id"]}")

            order["status"] = OrderStatus.READY.value
            self.order_queue.task_done()

    def monitoring(self):
        self.kitchen_ready.wait()
        while self.system_running:
            with self.stats_lock:
                total_orders = self.stats["total_orders"]
                completed_orders = self.stats["completed_orders"]
                average_cooking_time = f"{self.stats["cooking_time_total"] / self.stats["completed_orders"]:.2f}" if self.stats["completed_orders"] > 0 else 0
                
            in_queue = self.order_queue.qsize()
            available_stoves = self.available_stoves
            record_date = datetime.now().strftime("%d/%m, %H:%M:%S")

            stats_record = {
                "Всего заказов": total_orders,
                "Выполнено": completed_orders,
                "В очереди": in_queue,
                "Среднее время приготовления блюд": average_cooking_time,
                "Количество свободных конфорок": available_stoves,
                "Дата": record_date
            }

            with open("restaurant_record", "a", encoding="utf-8") as f:
                json.dump(stats_record, f, ensure_ascii=False)
                f.write("\n")
            print("Статистика: сохранена запись статистики")

            time.sleep(5)


    def start_system(self):
        print("ЗАПУСК СИСТЕМЫ РЕСТОРАНА...")

        self.system_running = True

        preparation_thread = threading.Thread(target=self.kitchen_preparation)
        preparation_thread.start()
        preparation_thread.join()
        
        for i in range(4):
            producer_thread = threading.Thread(target=self.order_producer, args=(i+1, ))
            producer_thread.start()
            self.producers.append(producer_thread)

        for i in range(3):
            consumer_thread = threading.Thread(target=self.chef_consumer, args=(i+1, ))
            consumer_thread.start()
            self.consumers.append(consumer_thread)

        monitoring_thread = threading.Thread(target=self.monitoring, daemon=True)
        monitoring_thread.start()

    def stop_system(self):
        print("ЗАКРЫТИЕ РЕСТОРАНА...")

        self.system_running = False
        
        for producer in self.producers:
            producer.join()

        for consumer in self.consumers:
            consumer.join()

        with self.stats_lock:
            total_orders = self.stats["total_orders"]
            completed_orders = self.stats["completed_orders"]
            average_cooking_time = f"{self.stats["cooking_time_total"] / self.stats["completed_orders"]:.2f}" if self.stats["completed_orders"] > 0 else 0
        
        print(f"""
ИТОГИ ДНЯ!
Всего принято заказов: {total_orders}
Успешно выполнено: {completed_orders}
Среднее время приготовления: {average_cooking_time}
              """)

        print("РЕСТОРАН ЗАКРЫТ!")


if __name__ == "__main__":
    restaurant = OrderSystem()

    try:
        restaurant.start_system()

        time.sleep(60)

        restaurant.stop_system()

    except KeyboardInterrupt:
        print("!ЭКСТРЕННОЕ ЗАКРЫТИЕ!")
        restaurant.stop_system()