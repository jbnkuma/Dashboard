from novell_libraries.dashboard_utils import FileConfig

"""
    :author: Jesus Becerril Navarrete
    :organization: 
    :contact: jesusbn5@protonmail.com

"""

__docformat__ = "restructuredtext"

data_conf = FileConfig().db_config()
environment_data = FileConfig().environment_data()
DEBUG = environment_data[0]
ECHO = environment_data[6]
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s/reports' % (data_conf[0], data_conf[1], data_conf[2])
SECRET_KEY = environment_data[1]  # Create your own.
SESSION_PROTECTION = environment_data[2]
UPLOAD_FOLDER = environment_data[3]
ALLOWED_EXTENSIONS = environment_data[4].split(",")
CMD_RUBY = FileConfig.cmd()
USERS_FILE = FileConfig.user_log_file()
