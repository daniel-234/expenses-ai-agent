class ExpenseNotFoundError(Exception):
    def __init__(self, id):
        super().__init__(id)
        self.id = id

    def __str__(self):
        return f"ID {self.id} was not found in expenses"
