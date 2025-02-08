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


class UpdateItemsError(ItemsLoaderError):
    pass
