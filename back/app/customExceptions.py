class ItemsLoaderError(Exception):
    pass


class JsonFetchError(ItemsLoaderError):
    pass


class JsonParseError(ItemsLoaderError):
    pass


class UpdateTagsError(ItemsLoaderError):
    pass


class UpdateStatsError(ItemsLoaderError):
    pass


class UpdateEffectsError(ItemsLoaderError):
    pass


class UpdateItemsError(ItemsLoaderError):
    pass


class ProcessOrderException(Exception):
    pass


class InvalidItemException(ProcessOrderException):
    pass


class UserIdNotFound(ProcessOrderException):
    def __init__(self, userName: str, message: str):
        self.userName = userName
        self.message = message
        super().__init__(message)

    pass


class DifferentTotal(ProcessOrderException):
    def __init__(self, originalTotal, databaseTotal, message):
        self.originalTotal = originalTotal
        self.databaseTotal = databaseTotal
        super().__init__(message)

    pass


class OrderNotFoundException(ProcessOrderException):
    pass


class NotEnoughGoldException(ProcessOrderException):
    pass


class ProfileWorkerException(Exception):
    pass


class UserNoGoldRow(ProfileWorkerException):
    pass

class InvalidUserNameException(Exception):
    pass

class InvalidUserEmailException(Exception):
    pass

class InvalidUserGoldFieldException(Exception):
    pass
