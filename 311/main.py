import json
from reader import DataReader
from strategies import ConsoleOutputStrategy, FileOutputStrategy, RedisOutputStrategy, KafkaOutputStrategy

def get_strategy(strategy_name: str):
    """Фабрика: вибирає стратегію на основі переданого імені"""
    strategy_name = strategy_name.lower()
    
    if strategy_name == "redis":
        return RedisOutputStrategy()
    elif strategy_name == "kafka":
        return KafkaOutputStrategy()
    elif strategy_name == "file":
        return FileOutputStrategy()
    else:
        return ConsoleOutputStrategy()

def get_user_choice():
    """Виводить інтерактивне меню в термінал"""
    print("\n" + "="*40)
    print(" 🛠️  ВИБІР СТРАТЕГІЇ ЗБЕРЕЖЕННЯ ДАНИХ ")
    print("="*40)
    print("  1. Вивести в консоль (Console)")
    print("  2. Зберегти у файл (JSON File)")
    print("  3. Відправити у Redis (Docker)")
    print("  4. Відправити у Kafka (Docker)")
    print("-" * 40)
    
    while True:
        choice = input("Оберіть номер (1-4) або натисніть Enter (взяти з config.json): ")
        
        if choice == '1': return "console"
        if choice == '2': return "file"
        if choice == '3': return "redis"
        if choice == '4': return "kafka"
        if choice == '': return None # Повертаємо None, щоб тригернути config.json
        
        print("❌ Невірний вибір. Введіть цифру від 1 до 4.")

def main():
    # 1. Читаємо конфіг для шляху до CSV та базових налаштувань
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 2. Запитуємо користувача через термінал
    user_strategy = get_user_choice()
    
    # 3. Визначаємо фінальну стратегію (пріоритет за терміналом)
    if user_strategy is None:
        active_strategy_name = config.get('output_strategy', 'console')
        print(f"\n[INFO] Використовуємо налаштування з config.json: {active_strategy_name.upper()}")
    else:
        active_strategy_name = user_strategy
        print(f"\n[INFO] Ви обрали стратегію вручну: {active_strategy_name.upper()}")

    # 4. Створюємо об'єкти
    reader = DataReader(config['csv_file_path'])
    strategy = get_strategy(active_strategy_name)

    print(f"\n--- Старт обробки ---")

    try:
        # Вичитуємо з CSV і відправляємо в обрану стратегію
        for row in reader.read_data():
            strategy.send_data(row)
    except FileNotFoundError:
        print(f"❌ Помилка: Файл {config['csv_file_path']} не знайдено!")
    except Exception as e:
        print(f"❌ Помилка під час обробки: {e}")
    finally:
        # Обов'язково закриваємо стратегію (щоб зберігся файл або закрилась Кафка)
        strategy.close()

    print("-" * 30)
    print("✅ Всі рядки успішно оброблено!")

if __name__ == "__main__":
    main()