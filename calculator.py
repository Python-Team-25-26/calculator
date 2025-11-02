import re
from typing import List, Tuple
import logging

class Calculator:
    PRIORITY = {
        '+': 1, '-': 1,
        '*': 2, '/': 2,
        '^': 3,
    }
    
    def __init__(self):
        self.previous_result = None
        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def tokenize(self, expression: str) -> List[str]:
        pattern = r'''
            \d+\.?\d*  |  # числа
            \.\d+      |  # числа начинающиеся с точки
            [+\-*/^()] |  # операторы и скобки
            _          |  # предыдущий результат
            inf        |  # бесконечность
            nan           # не число
        '''
        tokens = re.findall(pattern, expression, re.VERBOSE | re.IGNORECASE)
        tokens = [token for token in tokens if token.strip()]
        self.logger.info(f"Токенизация: {expression} -> {tokens}")
        return tokens
    
    def is_number(self, token: str) -> bool:
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def to_number(self, token: str) -> float:
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
        left, tokens = self.parse_primary(tokens)
        
        while tokens and tokens[0] in self.PRIORITY:
            operator = tokens[0]
            if self.PRIORITY[operator] < min_priority:
                break

            next_precedence = self.PRIORITY[operator] + 1 if operator != '^' else self.PRIORITY[operator]
            
            right, tokens = self.parse_expression(tokens[1:], next_precedence)
            left = self.apply_operator(operator, left, right)
        
        return left, tokens

    def parse_primary(self, tokens: List[str]) -> Tuple[float, List[str]]:
        if not tokens:
            self.logger.error("Неожиданный конец выражения")
            return float('nan'), []
        
        token = tokens[0]
        
        if token == '+':
            right, remaining = self.parse_primary(tokens[1:])
            return right, remaining
        
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
            expression = expression.replace(' ', '').lower()
            
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