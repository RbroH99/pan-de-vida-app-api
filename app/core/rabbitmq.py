"""
RabbitMQ middlewares for the API
"""
import aio_pika, logging, asyncio, json

from django.contrib.auth import get_user_model

from app.settings import RABBITMQ_URL

from asgiref.sync import sync_to_async


def create_user(user_info):
     """Syncronusly creates a new user."""
     get_user_model().objects.create_user(
          id=user_info["id"],
          email=user_info["email"]
     )


create_user_async = sync_to_async(
     create_user,
     thread_sensitive=True)


async def start_consuming():
        """Starts de RabbitMQ consumer with aio-pika."""
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        queue = await channel.declare_queue('user_created', durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    user_info = message.body.decode()
                    print(f" MAIN API Received {user_info}")

                    user_info = json.loads(user_info)
                    await create_user_async(user_info)
                    print(f" User {user_info['email']} created")


async def secure_start_consuming():
     """Try to start RabbitMQ consumer handling errors."""
     rabbitmq_up = False
     counter = 0

     while rabbitmq_up is False or \
         counter == 5:
         try:
             logging.info('RabbitMQ consummer will start in 1 min...')
             await asyncio.sleep(30)
             logging.info('Starting RabbitMQ consummer...')
             await start_consuming()
             rabbitmq_up = True
         except Exception as e:
             logging.exception('Error starting RabbitMQ consumer: {e}')
             logging.info('Retrying connection in a minute...')
             await asyncio.sleep(30)
             counter+=1

     if rabbitmq_up is True:
         logging.info('RabbitMQ connection success!')
     else:
         logging.critical('Unable to connect to RabbitMQ')
