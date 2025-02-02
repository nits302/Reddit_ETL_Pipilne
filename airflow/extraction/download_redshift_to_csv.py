import configparser
import pathlib
import psycopg2
from psycopg2 import sql
import csv
import sys
import os

"""
Download Redshift table to CSV file. Will be stored under /tmp folder.
"""

# Parse configuration file
script_path = pathlib.Path(__file__).parent.resolve()
parser = configparser.ConfigParser()
parser.read(f"{script_path}/configuration.conf")

# Store configuration variables
USERNAME = parser.get("aws_config", "redshift_username")
PASSWORD = parser.get("aws_config", "redshift_password")
HOST = parser.get("aws_config", "redshift_hostname")
PORT = parser.get("aws_config", "redshift_port")
DATABASE = parser.get("aws_config", "redshift_database")
TABLE_NAME = "reddit"


def connect_to_redshift():
    """
    Connect to Redshift and return connection. This is a wrapper around psycopg2. connect that does not raise exceptions.


    @return A connection to Redshift. If there is an error the program exits with an error code. Otherwise the connection is returned
    """

    try:
        rs_conn = psycopg2.connect(
            dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOST, port=PORT
        )
        return rs_conn
    except Exception as e:
        print(f"Unable to connect to Redshift. Error {e}")
        sys.exit(1)


def download_redshift_data(rs_conn):
    """
    Download data from Redshift table to CSV file.

    @param rs_conn - Connection to Redshift database
    """
    # Tạo thư mục output nếu chưa tồn tại
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with rs_conn:
        cur = rs_conn.cursor()
        cur.execute(
            sql.SQL("SELECT * FROM {table};").format(table=sql.Identifier(TABLE_NAME))
        )
        result = cur.fetchall()
        headers = [col[0] for col in cur.description]
        result.insert(0, tuple(headers))

        # Sử dụng os.path.join để tạo đường dẫn phù hợp với hệ điều hành
        output_file = os.path.join(output_dir, "redshift_output.csv")

        with open(output_file, "w", newline="") as fp:
            myFile = csv.writer(fp)
            myFile.writerows(result)


# Download the redshift data from the server
if __name__ == "__main__":
    rs_conn = connect_to_redshift()
    download_redshift_data(rs_conn)
