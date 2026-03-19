import json
from reader import DataReader
from strategies import ConsoleOutputStrategy, FileOutputStrategy, RedisOutputStrategy, KafkaOutputStrategy, FireOutputStrategy

def get_strategy(strategy_name: str, config: dict):
    strategy_name = strategy_name.lower()
    
    if strategy_name == "redis":
        return RedisOutputStrategy()
    elif strategy_name == "kafka":
        return KafkaOutputStrategy()
    elif strategy_name == "file":
        return FileOutputStrategy()
    elif strategy_name == "firebase":
        return FireOutputStrategy(config.get("firebase_url", ""))
    else:
        return ConsoleOutputStrategy()

def get_user_choice():
    print("\n" + "="*40)
    print(" ВИБІР СТРАТЕГІЇ ЗБЕРЕЖЕННЯ ДАНИХ ")
    print("="*40)
    print("  1. Вивести в консоль")
    print("  2. Зберегти у файл")
    print("  3. Відправити у Redis (Docker)")
    print("  4. Відправити у Kafka (Docker)")
    print("  5. Відправити у Firebase")
    print("-" * 40)
    
    while True:
        choice = input("Оберіть номер (1-5) або натисніть Enter (взяти з config.json): ")
        
        if choice == '1': return "console"
        if choice == '2': return "file"
        if choice == '3': return "redis"
        if choice == '4': return "kafka"
        if choice == '5': return "firebase"
        if choice == '': return None
        
        print("Невірний вибір. Введіть цифру від 1 до 5.")

def main():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    user_strategy = get_user_choice()
    
    if user_strategy is None:
        active_strategy_name = config.get('output_strategy', 'console')
        print(f"\n[INFO] Використовуємо налаштування з config.json: {active_strategy_name.upper()}")
    else:
        active_strategy_name = user_strategy
        print(f"\n[INFO] Ви обрали стратегію вручну: {active_strategy_name.upper()}")

    reader = DataReader(config['csv_file_path'])
    strategy = get_strategy(active_strategy_name, config)

    print(f"\n--- Старт обробки ---")

    try:
        for row in reader.read_data():
            strategy.send_data(row)
            
    except FileNotFoundError:
        print(f"Помилка: Файл {config['csv_file_path']} не знайдено!")
        
    except KeyboardInterrupt:
        print("\nОбробку перервано користувачем (Ctrl+C).")
        
    except Exception as e:
        print(f"Помилка під час обробки: {e}")
        
    finally:
        strategy.close()

    print("-" * 30)
    print("Всі рядки успішно оброблено!")

if __name__ == "__main__":
    main()