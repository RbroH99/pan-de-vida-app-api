"""
Custom Middleware for Main API.
"""
from django.utils.deprecation import MiddlewareMixin

from .rabbitmq import secure_start_consuming

import threading
import asyncio
import os


#Verify if enviroment is gitHub action
CI_ENV = os.environ.get('CI_ENV')


class RabbitMQConsumerMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        #Verify env before starting consumer.
        if CI_ENV != "true":
            self.start_consumer_thread()
        else:
            print("CI_ENV is set to true, RabbitMQ consumer will not run.")

    def start_consumer_thread(self):
        consumer_thread = threading.Thread(target=self.run_consumer)
        consumer_thread.start()

    def run_consumer(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(secure_start_consuming())
