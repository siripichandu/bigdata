import pymysql
import yaml


def load_config():
    """Load configuration from the YAML file.

    Returns:
        dict: Configuration data.
    """
    with open("api_demo/config_template.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()


def get_mysql_connection():
    """Create a MySQL connection using the configuration.

    Returns:
        Connection: MySQL connection object.
    """
    return pymysql.connect(
        host=config["mysql"]["host"],
        port=config["mysql"]["port"],
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        db=config["mysql"]["database"],
    )
