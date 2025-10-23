import re
import math
from typing import List, Tuple

class Calculator:
    def __init__(self):
        self.previous_result = None
        self.setup_logging()

    def setup_logging(self):
        import logging
        self.logger = logging.getLogger(__name__)

    def tokenize(self, expression: str) -> List[str]:
        """Разбивает выражение на токены"""
        pattern = r'''
            \d+\.?\d*  |  # числа
            \.\d+      |  # числа начинающиеся с точки
            [+\-*/^()] |  # операторы и скобки
            _          |  # предыдущий результат
            inf        |  # бесконечность
            \+inf      |  # положительная бесконечность  
            -inf       |  # отрицательная бесконечность
            nan           # не число
        '''
        re.compile(pattern)
        tokens = re.findall(pattern, expression, re.VERBOSE | re.IGNORECASE)
        tokens = [token.strip() for token in tokens if token.strip()]
        
        self.logger.info(f"Токенизация: {expression} -> {tokens}")
        return tokens
    
    def is_number(self, token: str) -> bool:
        if token.lower() in ['inf', '+inf', '-inf', 'nan']:
            return True
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def to_number(self, token: str) -> float:
        token_lower = token.lower()
        if token_lower == 'inf' or token_lower == '+inf':
            return float('inf')
        elif token_lower == '-inf':
            return float('-inf')
        elif token_lower == 'nan':
            return float('nan')
        else:
            return float(token)
    
    def apply_operator(self, operator: str, left: float, right: float) -> float:
        self.logger.debug(f"Применение оператора: {left} {operator} {right}")
        
        try:
            match operator:
                case '+':
                    result = left + right
                case '-':
                    result = left - right
                case '*':
                    result = left * right
                case '/':
                    if right == 0:
                        if left == 0:
                            result = float('nan')
                        elif left > 0:
                            result = float('inf')
                        elif left < 0:
                            result = float('-inf')
                        else:
                            result = left / right
                    else:
                        result = left / right
                case '^':
                    if left == 0 and right < 0:
                        result = float('inf')
                    else:
                        result = left ** right
                case _:
                    raise ValueError(f"Неизвестный оператор: {operator}")
            
            self.logger.debug(f"Результат операции: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при применении оператора {operator}: {e}")
            return float('nan')
        

    def parse_expression(self, tokens: List[str], min_priority: int = 1) -> Tuple[float, List[str]]:
        PRIORITY = {
            '+': 1, '-': 1,
            '*': 2, '/': 2,
            '^': 3,        
        }
        
        left, tokens = self.parse_primary(tokens)
        
        while tokens and tokens[0] in PRIORITY:
            operator = tokens[0]
            if PRIORITY[operator] < min_priority:
                break
            
            next_precedence = PRIORITY[operator] + 1 if operator == '^' else PRIORITY[operator]
            right, tokens = self.parse_expression(tokens[1:], next_precedence)
            left = self.apply_operator(operator, left, right)
        
        return left, tokens

    def parse_primary(self, tokens: List[str]) -> Tuple[float, List[str]]:
        if not tokens:
            self.logger.error("Неожиданный конец выражения")
            return float('nan'), []
        
        token = tokens[0]
        if token == '-':
            right, remaining = self.parse_primary(tokens[1:])
            return -right, remaining
        
        if token == '(':
            result, remaining = self.parse_expression(tokens[1:])
            if remaining and remaining[0] == ')':
                return result, remaining[1:]
            self.logger.error("Незакрытая скобка")
            return float('nan'), []
        
        if token == '_':
            if self.previous_result is None:
                self.logger.warning("Попытка использовать предыдущий результат, но он не определен")
                return 0.0, tokens[1:]
            return self.previous_result, tokens[1:]
        
        if self.is_number(token):
            return self.to_number(token), tokens[1:]
        
        self.logger.error(f"Неожиданный токен: {token}")
        return float('nan'), tokens[1:]
        

    def calculate(self, expression: str) -> float:
        self.logger.info(f"Вычисление выражения: {expression}")
        
        try:
            expression = expression.replace(' ', '')
            
            if not expression:
                self.logger.warning("Пустое выражение")
                return 0.0
            
            tokens = self.tokenize(expression)
            
            if not tokens:
                self.logger.warning("Не удалось разобрать выражение на токены")
                return 0.0
            
            result, remaining_tokens = self.parse_expression(tokens)
            
            if remaining_tokens:
                self.logger.warning(f"Необработанные токены: {remaining_tokens}")
            
            self.previous_result = result
            
            self.logger.info(f"Результат вычисления: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при вычислении: {e}")
            return float('nan')




def main():
    calc = Calculator()
    calc.logger.info("Калькулятор запущен")
    
    print("Интерактивный калькулятор")
    print("Введите 'quit' для выхода")
    print("-" * 40)
    
    while True:
        try:
            expression = input("> ").strip()
            
            if expression.lower() in ['quit', 'exit', 'q']:
                calc.logger.info("Калькулятор завершил работу")
                break
            
            if not expression:
                continue
            
            result = calc.calculate(expression)
            print(f"Результат: {result}")
            print()
            
        except KeyboardInterrupt:
            calc.logger.info("Работа прервана пользователем")
            break
        except Exception as e:
            calc.logger.error(f"Неожиданная ошибка: {e}")
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()