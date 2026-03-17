import json
from reader import DataReader
from strategies import ConsoleOutputStrategy, RedisOutputStrategy, KafkaOutputStrategy, FileOutputStrategy

def get_strategy(config: dict):
    """Вибирає потрібний клас на основі слова з конфігу"""
    strategy_name = config.get('output_strategy', 'console').lower()
    
    if strategy_name == "redis":
        return RedisOutputStrategy()
    elif strategy_name == "kafka":
        return KafkaOutputStrategy()
    elif strategy_name == "file":
        return FileOutputStrategy()
    else:
        return ConsoleOutputStrategy()

def main():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    reader = DataReader(config['csv_file_path'])
    strategy = get_strategy(config)

    print(f"--- Старт ---")
    print(f"Активна стратегія: {config['output_strategy'].upper()}")
    print("-" * 30)

    try:
        for row in reader.read_data():
            strategy.send_data(row)
    except FileNotFoundError:
        print(f"Помилка: Файл {config['csv_file_path']} не знайдено!")
    except Exception as e:
        print(f"Помилка під час обробки: {e}")
    finally:
        strategy.close()

    print("-" * 30)
    print("Всі рядки оброблено!")

if __name__ == "__main__":
    main()