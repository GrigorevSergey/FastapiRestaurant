import random
from typing import Dict
from datetime import datetime, timedelta

class SMSService:
    _instance = None
    _storage: Dict[str, dict] = {} 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SMSService, cls).__new__(cls)
        return cls._instance

    def generate_code(self) -> str:
        return str(random.randint(1000, 9999))

    def _clean_old_codes(self):
        """Очищает коды старше 5 минут"""
        now = datetime.now()
        self._storage = {
            phone: data for phone, data in self._storage.items()
            if now - data["created_at"] < timedelta(minutes=5)
        }

    async def send_sms(self, phone: str) -> None:
        try:
            self._clean_old_codes()
            code = self.generate_code()
            self._storage[phone] = {
                "code": code,
                "created_at": datetime.now()
            }
            print(f"SMS код для {phone}: {code}")
        except Exception as e:
            print(f"Ошибка при отправке SMS: {str(e)}")
            raise ValueError("Ошибка при отправке SMS")

    async def verify_code(self, phone: str, code: str) -> bool:
        try:
            self._clean_old_codes()
            data = self._storage.get(phone)
            if not data:
                print(f"Код для {phone} не найден или истек")
                return False
                
            stored_code = data["code"]
            print(f"Проверка кода для {phone}: получен {code}, сохранен {stored_code}")
            
            if stored_code == code:
                self._storage.pop(phone, None)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при проверке кода: {str(e)}")
            return False