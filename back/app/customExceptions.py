class ItemsLoaderError(Exception):
    pass


class SameVersionUpdateError(ItemsLoaderError):
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


class InvalidPasswordException(Exception):
    pass


class CartProcessorException(Exception):
    pass


class DeliveryDateAssignerException(Exception):
    pass


class ItemNotFoundException(DeliveryDateAssignerException):
    pass


class DeliveryDateAssignmentError(DeliveryDateAssignerException):
    pass


class LocationManagerException(Exception):
    pass


class LocationNotFoundException(LocationManagerException):
    pass


class LocationAlreadyExistsException(LocationManagerException):
    pass


class LocationUpdateError(LocationManagerException):
    pass


class LocationDeleteError(LocationManagerException):
    pass


class ReviewProcessorException(Exception):
    pass


class InvalidRatingException(ReviewProcessorException):
    pass


class InvalidUserReview(ReviewProcessorException):
    pass


class DataGeneratorException(Exception):
    pass


class LocationGenerationError(DataGeneratorException):
    pass


class UserGenerationError(DataGeneratorException):
    pass


class OrderGenerationError(DataGeneratorException):
    pass


class OrderItemAssociationError(DataGeneratorException):
    pass


class ReviewGenerationError(DataGeneratorException):
    pass


class CommentGenerationError(DataGeneratorException):
    pass
