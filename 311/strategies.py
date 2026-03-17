import json
from abc import ABC, abstractmethod

class OutputStrategy(ABC):
    @abstractmethod
    def send_data(self, data: dict):
        pass

    def close(self):
        pass

class ConsoleOutputStrategy(OutputStrategy):
    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        category = data.get('Category', 'Unknown')
        print(f"[CONSOLE] Звернення ID: {case_id} | Категорія: {category}")

class RedisOutputStrategy(OutputStrategy):
    def __init__(self, host='localhost', port=6379):
        import redis
        print(f"🔄 [REDIS] Підключення до локального Docker ({host}:{port})...")
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.client.ping()
        print("✅ [REDIS] З'єднання успішно встановлено!\n")

    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        self.client.set(f"case:{case_id}", json.dumps(data, ensure_ascii=False))
        print(f"🗄️ [REDIS] Збережено в базу: case:{case_id}")

class KafkaOutputStrategy(OutputStrategy):
    def __init__(self, bootstrap_servers='localhost:9092', topic='sf_311_cases'):
        from kafka import KafkaProducer
        print(f"🔄 [KAFKA] Підключення до брокера Kafka ({bootstrap_servers})...")
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        print("✅ [KAFKA] Продюсер налаштований!\n")

    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        self.producer.send(self.topic, data)
        print(f"🚀 [KAFKA] Відправлено в топік: Case ID {case_id}")
        
    def close(self):
        self.producer.flush()
        self.producer.close()

class FileOutputStrategy(OutputStrategy):
    def __init__(self, output_filename="output_data.json"):
        self.output_filename = output_filename
        self.data_list = []
        print(f"🔄 [FILE] Підготовка до запису у файл {self.output_filename}...")

    def send_data(self, data: dict):
        self.data_list.append(data)
        
    def close(self):
        with open(self.output_filename, 'w', encoding='utf-8') as f:
            json.dump(self.data_list, f, ensure_ascii=False, indent=4)
        print(f"📁 [FILE] Всі дані успішно збережено у файл {self.output_filename}!")
