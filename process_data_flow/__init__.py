from process_data_flow.rabbitmq_config import RabbitMQConfig

rabbitmq_config = RabbitMQConfig()
rabbitmq_config.client.connection.close()
