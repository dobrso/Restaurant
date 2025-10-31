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
        # сигнал, что кухня готова к работе (типа ресторан открывается)
        self.kitchen_ready = threading.Event()

        # для управления доступом к плите (ограниченное количество мест)
        self.stove_condition = threading.Condition()
        self.available_stoves = 2  # всего 2 конфорки :( Мы бедный ресторан

        # очередь заказов
        self.order_queue = queue.Queue(maxsize=10)

        # статистика
        self.stats = {
            "total_orders": 0,
            "completed_orders": 0,
            "failed_orders": 0,
            "cooking_time_total": 0
        }
        self.stats_lock = threading.Lock()

        # флаг работы системы
        self.system_running = False

        # потоки
        self.producers = []
        self.consumers = []
        self.monitor_thread = None

    # функция подготовки кухни, при открытии ресторана, кухня сначала готовится
    def kitchen_preparation(self):
        print("ПОВАР: Начинаю подготовку кухни...")

        # имитация подготовки
        tasks = [
            "Проверяю оборудование",
            "Настраиваю температуру плит",
            "Подготавливаю ингредиенты",
            "Запускаю вытяжку"
        ]

        # TODO: Выполняем подготовительные действия и сообщаем поварам и официантам "ОТКРЫВАЕМСЯ!!!"

    # функция для генерации заказов (то есть наши официанты). Не забываем, что ресторан должен быть открыт!
    def order_producer(self, producer_id):

        menu_items = [
            # придумайте пулл блюд, с которыми будут генерироваться заказы
        ]

        while self.system_running:
            order = {
                "order_id": random.randint(1000, 9999),
                "customer_id": random.randint(1, 100),
                "dish": random.choice(menu_items),
                "complexity": random.randint(1, 5),  # сложность приготовления 1-5
                "status": OrderStatus.PENDING.value,
                "created_time": datetime.now(),
                "producer_id": producer_id
            }

            # TODO: Официант принимает заказ (мы его генерируем), отправляет поварам (не забываем про подсчет статистики)

            time.sleep(random.uniform(0.5, 2))

    # функция для обработки заказов (наши поварята) - повар спрашивает повара... Не забываем, что ресторан должен быть открыт!
    def chef_consumer(self, chef_id):

        # TODO: Повар забирает заказ, проверяет есть ли свободная конфорка (если нет, то ждет, естественно), готовит по
        #  длительности в зависимости от сложности блюда cook_time = order["complexity"] * 0.5. Не забываем про статистику и статусы блюд!

        pass

    # Функция для демон-потока
    def monitoring(self):

        # TODO: Если рестик работает, каждые 5 секунд забираем статистику по параметрам:
        #  "Всего заказов",
        #  "Выполнено",
        #  "В очереди",
        #  "Среднее время приготовления блюд",
        #  "Количество свободных конфорок" и записываем статистику в файл со временем когда эта статистика была записана

        pass

    def start_system(self):
        print("ЗАПУСК СИСТЕМЫ РЕСТОРАНА...")

        # TODO: Запускаем нашу подготовку ресторана в отдельном потоке, ждем завершения и запускаем официантов и
        #  поваров, а также нашего демон-потока для статистики


    def stop_system(self):
        print("ЗАКРЫТИЕ РЕСТОРАНА...")

        # TODO: ждем когда все освободятся, выводим в консоль итоги рабочего дня:
        #  "Всего принято заказов",
        #  "Успешно выполнено",
        #  "Среднее время приготовления

        print("РЕСТОРАН ЗАКРЫТ!")


# Запуск системы
if __name__ == "__main__":
    restaurant = OrderSystem()

    try:
        restaurant.start_system()

        # работаем 60 секунд
        time.sleep(60)

        restaurant.stop_system()

    except KeyboardInterrupt:
        print("!ЭКСТРЕННОЕ ЗАКРЫТИЕ!")
        restaurant.stop_system()