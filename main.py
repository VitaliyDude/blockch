import os
import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        # Инициализация цепочки блоков и текущих транзакций
        self.chain = []
        self.current_transactions = []

        # Создаем блок-генезис
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof, previous_hash=None):
        # Создание нового блока
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }

        # Сохраняем блок в файл, если он новый или изменен
        if not self.block_exists(block) or self.is_block_changed(block):
            self.save_block_to_file(block)

        # Очищаем список текущих транзакций
        self.current_transactions = []

        # Добавляем блок в цепочку
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Добавление новой транзакции в список текущих транзакций
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        # Получение последнего блока в цепочке
        return self.chain[-1] if self.chain else None

    @staticmethod
    def hash(block):
        # Преобразование блока в строку JSON и хеширование с использованием SHA-256
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # Поиск подходящего значения proof для нового блока
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # Проверка условия нахождения хеша с определенным числом нулей в начале
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def save_block_to_file(self, block):
        # Папка для сохранения блоков
        blocks_folder = "C:\\Blockchain\\blocks"
        if not os.path.exists(blocks_folder):
            os.makedirs(blocks_folder)

        # Имя файла на основе индекса блока
        file_path = os.path.join(blocks_folder, f"block_{block['index']}.txt")

        # Запись блока в файл
        with open(file_path, 'w') as file:
            file.write(json.dumps(block, indent=2))

    def block_exists(self, block):
        # Проверка существования файла блока
        file_path = os.path.join("C:\\Blockchain\\blocks", f"block_{block['index']}.txt")
        return os.path.exists(file_path)

    def is_block_changed(self, block):
        # Проверка, был ли блок изменен после сохранения
        file_path = os.path.join("C:\\Blockchain\\blocks", f"block_{block['index']}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                saved_block = json.load(file)
                return self.hash(saved_block) != self.hash(block)
        return False

    def validate_chain(self):
        # Проверка целостности цепочки блоков
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Пересчитываем хеш предыдущего блока
            recalculated_previous_hash = self.hash(previous_block)

            # Проверяем хеш предыдущего и текущего блока
            if block['previous_hash'] != recalculated_previous_hash or self.is_block_changed(block):
                return False

            # Пересчитываем доказательство работы и проверяем его
            if not self.valid_proof(previous_block['proof'], block['proof']):
                return False
        return True


# Пример использования
blockchain = Blockchain()
blockchain.new_transaction("Alice", "Bob", 2)
last_block = blockchain.last_block
last_proof = last_block['proof']
proof = blockchain.proof_of_work(last_proof)
block = blockchain.new_block(proof)

# Проверяем цепочку на целостность (должно быть валидно)
if blockchain.validate_chain():
    print("Цепочка блоков валидна.")
else:
    print("Ошибка в цепочке блоков.")

# Теперь предположим, что кто-то пытается изменить данные в блоке (меняем сумму транзакции в первой транзакции в первом блоке)
#blockchain.chain[1]['transactions'][0]['amount'] = 10

# Повторно проверяем цепочку на целостность (должна быть обнаружена ошибка)
if blockchain.validate_chain():
    print("Цепочка блоков валидна.")
else:
    print("Ошибка в цепочке блоков.")
