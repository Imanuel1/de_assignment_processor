# AI Tool Usage

## Tools I Used

[Gemini 3 Flash, IDE Autocomplete (GitHub Copilot)]

## What Helped Most

[
1. debug with docker-compose file and errors
2. RabbitMQ delayed logic for scheduling jobs, working with x-delayed-message plugin and also install it via Dockerfile
]

## What I Had to Fix

[
1. when i work with aio-pika library, it give an auto complete for a non existing functions, and also with docker-compose
2. suggested manually calling message.reject() inside an async with message.process() block. This caused an AttributeError or MessageProcessError because the context manager was trying to ack a message that I had already manually rejected
]

## What AI Struggled With

[
1. it forgot that variables defined in the init_rabbitmq function (like the exchange handle) aren't automatically available in the consumer callback. I had to manually implement a way to share the exchange state via app.state or function arguments
2. using auto complete is not correctly, for example: import faker from Faker and impoer random from random, and function that desn't exist
]
