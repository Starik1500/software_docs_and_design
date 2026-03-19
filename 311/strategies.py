import json
from abc import ABC, abstractmethod
import urllib.request

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

class FireOutputStrategy(OutputStrategy):
    def __init__(self, db_url: str):
        if not db_url:
            raise ValueError("Для Firebase потрібен URL бази даних у config.json!")
        
        self.db_url = db_url if db_url.endswith('/') else f"{db_url}/"
        print(f"Підключення до хмарної БД Google...")
        print("З'єднання налаштовано! Готово до відправки.\n")

    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        url = f"{self.db_url}cases/{case_id}.json"
        
        clean_data = {}
        for key, value in data.items():
            clean_key = key.replace('\t', '').replace('.', '_').replace('#', '_').replace('$', '_').replace('[', '_').replace(']', '_').strip()
            
            if isinstance(value, str):
                clean_value = value.replace('\t', '').strip()
            else:
                clean_value = value
                
            clean_data[clean_key] = clean_value
            
        payload = json.dumps(clean_data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='PUT')
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req) as response:
                print(f"🔥 [FIREBASE] Запис {case_id} успішно полетів у хмару!")
        except Exception as e:
            print(f"❌ [FIREBASE] Помилка відправки {case_id}: {e}")

    def close(self):
        print("\nУсі дані успішно завантажено на Firebase!")

