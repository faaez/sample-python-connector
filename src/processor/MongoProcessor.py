__author__ = "Nick Isaacs"
import multiprocessing
import logging
import random
from multiprocessing import queues
from pymongo import MongoClient
from src.processor.BaseProcessor import BaseProcessor

MONGO_COLLECTIONS = {"lncs":"lncs_combined_gnip","dietssds":"dietssds_decanted_gnip"}


class MongoProcessor(BaseProcessor):
    def __init__(self, _upstream, _enviroinment):
        BaseProcessor.__init__(self, _upstream, _enviroinment)
        self._collection = None

    def run(self):
        self.run_process.start()

    def _run(self):
        self.logr.debug("Mongo Processor Started")
        self.run_loop()

    def run_loop(self):
        while not self._stopped.is_set():
            payload = self.next_message()
            if not None == payload:
                payload['random'] = random.random()
                payload['after_gnip'] = True
                self.put_in_mongo(payload)
        self.logr.debug("Exiting Mongo run loop")

    def put_in_mongo(self, obj):
        self.logr.debug("Putting in Mongo: " + str(obj))
        for rule in obj['gnip']['matching_rules']:
            self.client()[rule['tag']].insert(obj)

    def client(self):
        if not self._client:
            host = self.environment.mongo_host
            port = int(self.environment.mongo_port)
            db = self.environment.mongo_db
            self._client = MongoClient(host=host, port=port)[db]
            self._client.authenticate(self.environment.mongo_username,self.environment.mongo_password)
        return self._client

    # def collection(self):
    #     if not self._collection:
    #         self._collection = self.environment.mongo_collection
    #     return self._collection

    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set() and self.queue.qsize() == 0

    def running(self):
        self.run_process.is_alive() and not self.stopped()

    def next_message(self):
        ret_val = None
        if self.queue.qsize() > 0:
            try:
                ret_val = self.queue.get(block=False)
            except multiprocessing.queues.Empty:
                self.logr.error("Queue was empty when trying to get next message")
        return ret_val
