class ItemsLoaderError(Exception):
    pass


class JSONFetchError(ItemsLoaderError):
    pass


class DataValidationError(ItemsLoaderError):
    pass


class NoDataNodeInJSON(ItemsLoaderError):
    pass


class TableUpdateError(ItemsLoaderError):
    def __init__(self, tableName:str, message:str | None = None):
        if message is None:
            message = f"Failed to update table:{tableName}"
        super().__init__(message)
        self.tableName = tableName
    pass
