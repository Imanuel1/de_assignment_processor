FROM rabbitmq:3.12-management

# Install curl to download the plugin
RUN apt-get update && apt-get install -y curl

# Download the plugin version that matches RabbitMQ 3.12.x
# Note: Using the official GitHub release URL
RUN curl -L https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v3.12.0/rabbitmq_delayed_message_exchange-3.12.0.ez > /opt/rabbitmq/plugins/rabbitmq_delayed_message_exchange-3.12.0.ez

# Enable the plugin
RUN rabbitmq-plugins enable --offline rabbitmq_delayed_message_exchange