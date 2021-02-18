# nice explanation of sending data to ES: https://towardsdatascience.com/exporting-pandas-data-to-elasticsearch-724aa4dd8f62
#TODO: prepare elasticsearch.yml, autoupdate index for faster search

from elasticsearch import Elasticsearch, helpers
import json
import logging

logger = logging.getLogger()


class ES:
    def __init__(self):
        self.es = Elasticsearch()

    def create_db(self, name: str):
        """
        Creates index in elasticsearch
        :param name: str, name of index
        :return: None
        """
        if not self.es.indices.exists(index='index'):
            with open('{name}.json','r') as f:
                doc = json.load(f)
            res = self.es.index(index=name, id=1, body=doc)
            logger.info('%s was created: %s' % (name, {res['result']}))
        else:
            logger.info('%s already exist' % name)

    def drop_db(self, name: str):
        """
        Deletes elasticsearch index
        :param name: str, name of index
        :return: None
        """
        res = self.es.indices.delete(index=name, ignore=[400, 404])
        logger.info(res)

    def overwrite_db(self, name: str):
        """
        checks if es index exist, if yes drops and creates a new one
        :param name: name of an index
        :return: None
        """

        if not self.es.indices.exists(index=name):
            self.create_db(name)
        else:
            self.drop_db(name)
            self.create_db(name)

    def bulk_load_data(self, name: str, docs: list):
        """
        inserts in bulk into es index
        :param name: name of the es index
        :param docs: list of dicts with data
        :return:
        """

        actions = [
            {
                "_index": name,
                "_type": "_doc",
                "_source": line,
                "_op_type": 'index', # kinda upsert
                "_id": line['id'] # then update works, using the movies id
            }
            for line in docs
        ]

        helpers.bulk(self.es, actions)