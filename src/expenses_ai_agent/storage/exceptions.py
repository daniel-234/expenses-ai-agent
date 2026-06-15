class ExpenseNotFoundError(Exception):
    def __init__(self, id: int):
        super().__init__(id)
        self.id = id

    def __str__(self) -> str:
        return f"ID {self.id} was not found in expenses"
