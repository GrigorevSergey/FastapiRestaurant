import random
from typing import Dict

class SMSService:
    _instance = None
    _storage: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SMSService, cls).__new__(cls)
        return cls._instance

    def generate_code(self):
        return str(random.randint(1000, 9999))

    def send_sms(self, phone: str):
        code = self.generate_code()
        self._storage[phone] = code
        print(f"SMS код для {phone}: {code}")

    def verify_code(self, phone: str, code: str) -> bool:
        stored_code = self._storage.get(phone)
        print(f"Проверка кода для {phone}: получен {code}, сохранен {stored_code}")
        return stored_code == code