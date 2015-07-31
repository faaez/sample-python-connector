__author__ = "Nick Isaacs"
import ConfigParser
import os
import logging.handlers
import logging
import sys

RELATIVE_CONFIG_PATH = "../../config/gnip.cfg"


class Envirionment(object):
    def __init__(self):
        # Just for reference, not all that clean right now
        self.config_file_name = None
        self.config = None
        self.streamname = None
        self.logfilepath = None
        self.logr = None
        self.rotating_handler = None
        self.username = None
        self.password = None
        self.streamurl = None
        self.filepath = None
        self.kwargs = None
        self.compressed = None
        self.rollduration = None
        self.processtype = None
        self.rollduration = None
        self.redis_host = None
        self.redis_port = None
        self.mongo_host = None
        self.mongo_port = None
        self.mongo_db = None
        self.mongo_username = None
        self.mongo_password = None
        self.kwargs = None # Ew

        self.logr = logging.getLogger('Environment')
        self.setup_config()
        self.setup_logs()


        self.streamname = self.config.get('stream', 'streamname')
        self.logr = logging.getLogger('Enviroinment Logger')
        self.rotating_handler = logging.handlers.RotatingFileHandler(
            filename=self.logfilepath + "/%s-log" % self.streamname,
            mode='a', maxBytes=2 ** 24, backupCount=5)
        self.rotating_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(funcName)s %(message)s"))
        self.logr.setLevel(logging.DEBUG)
        self.logr.addHandler(self.rotating_handler)
        if self.config.has_section('auth'):
            self.username = self.config.get('auth', 'username')
            self.password = self.config.get('auth', 'password')
        elif self.config.has_section('creds'):
            self.username = self.config.get('creds', 'username')
            self.password = self.config.get('creds', 'password')
        else:
            self.logr.error("No credentials found")
            sys.exit()
        self.streamurl = self.config.get('stream', 'streamurl')
        self.filepath = self.config.get('stream', 'filepath')
        self.kwargs = {}
        if self.config.has_section('db'):
            self.kwargs["sql_user_name"] = self.config.get('db', 'sql_user_name')
            self.kwargs["sql_password"] = self.config.get('db', 'sql_password')
            self.kwargs["sql_instance"] = self.config.get('db', 'sql_instance')
            self.kwargs["sql_db"] = self.config.get('db', 'sql_db')
        if self.config.has_section('gnacs'):
            self.kwargs["options"] = self.config.get('gnacs', 'options')
            self.kwargs["delim"] = self.config.get('gnacs', 'delim')
        try:
            self.compressed = self.config.getboolean('stream', 'compressed')
        except ConfigParser.NoOptionError:
            self.compressed = True
        self.logr.info("Collection starting for stream %s" % self.streamurl)
        self.logr.info("Storing data in path %s" % self.filepath)
        self.rollduration = int(self.config.get('proc', 'rollduration'))
        processtype = self.config.get('proc', 'processtype')
        self.logr.info("processing strategy %s" % processtype)

        # Redis
        if self.config.has_section('redis'):
            self.redis_host = self.config.get('redis', 'host')
            self.redis_port = self.config.get('redis', 'port')

        # Mongo
        if self.config.has_section('mongo'):
            self.mongo_host = self.config.get('mongo', 'host')
            self.mongo_port = self.config.get('mongo', 'port')
            self.mongo_db = self.config.get('mongo', 'db')
            self.mongo_username = self.config.get('mongo','username')
            self.mongo_password = self.config.get('mongo','password')
            # self.mongo_collection = self.config.get('mongo','collection')

    def setup_logs(self):
        relative_log_path = self.config.get('sys', 'logfilepath').strip(r'^/') or "log"
        _file = os.path.dirname(os.path.realpath(__file__))
        self.logr.debug(_file)
        root = os.path.join(_file, '../..')
        self.logfilepath = os.path.join(root, relative_log_path)
        try:
            os.mkdir(self.logfilepath)
        except OSError:
            # File exists
            pass
        self.logr.debug(self.logfilepath)

    def setup_config(self):
        if 'GNIP_CONFIG_FILE' in os.environ:
            self.config_file_name = os.environ['GNIP_CONFIG_FILE']
        else:
            dir = os.path.dirname(__file__)
            self.config_file_name = os.path.join(dir, RELATIVE_CONFIG_PATH)
            if not os.path.exists(self.config_file_name):
                self.logr.debug("No configuration file found.")
                sys.exit()
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file_name)
