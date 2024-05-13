"""
RabbitMQ middlewares for the API
"""
import aio_pika
import logging
import asyncio
import json

from django.http import Http404

from django.contrib.auth import get_user_model

from app.settings import RABBITMQ_URL

from asgiref.sync import sync_to_async


def create_user(user_info):
    """Syncronusly creates a new user."""
    superuser = user_info.pop('is_superuser', None)
    if not superuser:
        get_user_model().objects.create_user(
             id=user_info["id"],
             email=user_info["email"]
        )
    else:
        get_user_model().objects.create_superuser(
            id=user_info["id"],
            email=user_info["email"],
            password=user_info["password"]
        )


def update_user(user_info):
    """Syncronusly updates a existing user."""
    try:
        user = get_user_model().objects.get(id=user_info["id"])
    except get_user_model().DoesNotExist:
        raise Http404("Item does not exist")

    password = user_info.pop("password", None)
    email = user_info.get("email", None)

    if password:
        user.password = password
    if email != user.email:
        user.email = email

    user.save()


create_user_async = sync_to_async(
    create_user,
    thread_sensitive=True)


update_user_async = sync_to_async(
    update_user,
    thread_sensitive=True)


async def start_consuming():
    """Starts consuming from both 'user_created' and 'user_modified' queues."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    user_created_queue = await channel.declare_queue(
        'user_created',
        durable=True
    )
    user_modified_queue = await channel.declare_queue(
        'user_modified',
        durable=True
    )

    user_created_iter = user_created_queue.iterator()
    user_modified_iter = user_modified_queue.iterator()

    async def process_user_created():
        async with user_created_iter:
            async for message in user_created_iter:
                async with message.process():
                    user_info = message.body.decode()
                    user_info = json.loads(user_info)
                    print(f"MAIN API Received {user_info['email']}.")
                    await create_user_async(user_info)
                    print(f"User {user_info['email']} created")

    async def process_user_modified():
        async with user_modified_iter:
            async for message in user_modified_iter:
                async with message.process():
                    user_info = message.body.decode()
                    user_info = json.loads(user_info)
                    print(f"MAIN API Received {user_info['email']}.")
                    await update_user_async(user_info)
                    print(f"User {user_info['email']} updated")

    await asyncio.gather(
        process_user_created(),
        process_user_modified()
    )

    await connection.close()


async def secure_start_consuming():
    """Try to start RabbitMQ consumer handling errors."""
    rabbitmq_up = False
    counter = 0

    while rabbitmq_up is False and counter < 2:
        try:
            logging.info('RabbitMQ consummer will start in 30s...')
            await asyncio.sleep(30)
            logging.info('Starting RabbitMQ consummer...')
            await start_consuming()
            rabbitmq_up = True
        except Exception as e:
            logging.exception(f'Error starting RabbitMQ consumer: {e}')
            logging.info('Retrying connection...')
            counter += 1

    if rabbitmq_up is True:
        logging.info('RabbitMQ connection success!')
    else:
        logging.critical('Unable to connect to RabbitMQ')
