import logging
from calculator import Calculator

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    file_formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(funcName)s:%(lineno)d] - [%(message)s]')
    
    console_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    
    file_handler = logging.FileHandler('calculator.log', encoding='UTF-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def main():
    setup_logging()
    
    calc = Calculator()
    calc.logger.info("Калькулятор запущен")    
    while True:
        try:
            expression = input("> ").strip()
            
            if expression.lower() in ['quit', 'exit', 'q']:
                calc.logger.info("Калькулятор завершил работу")
                break
            
            if not expression:
                continue
            
            result = calc.calculate(expression)
            print(f"{result}")
            
        except KeyboardInterrupt:
            calc.logger.info("Работа прервана пользователем")
            break
        except Exception as e:
            calc.logger.error(f"Неожиданная ошибка: {e}")
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()