class ItemsLoaderError(Exception):
    pass


class JSONFetchError(ItemsLoaderError):
    pass


class DataValidationError(ItemsLoaderError):
    pass


class NoDataNodeInJSON(ItemsLoaderError):
    pass


class TableUpdateError(ItemsLoaderError):
    pass
