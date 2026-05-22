class UnexpectedException(Exception):
    detail = "Неожиданная ошибка"
    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class ObjectAlreadyExists(UnexpectedException):
    detail = "Объект уже существует"