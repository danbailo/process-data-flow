from process_data_flow.commons.rabbitmq.consumer import (
    RabbitMQException,
)


class ItemAlreadyExists(RabbitMQException):
    message: str = 'Item already exists in database!'

    def __init__(
        self,
        message: str | None = None,
        requeue: bool | None = None,
    ) -> None:
        if not message:
            message = self.message
        super().__init__(message, requeue)
