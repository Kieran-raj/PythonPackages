"""Module to upload pdf statements"""
import os
from typing import Dict, List
from datetime import datetime

import pdfplumber
import sqlalchemy as db

from expenses_data_upload.helpers.mappings import category_conversion, month_conversion


class PdfScanner():
    """Class Docstring"""

    def __init__(self, file_location: str, sql_settings: Dict = None, is_mysql: bool = True,):
        self.file_location = file_location
        self.sql_settings = sql_settings
        self.is_mysql = is_mysql

    def get_raw_transactions(self):
        """Function Docstring"""
        raw_transactions = []
        for file in os.listdir(self.file_location):
            full_path = self.file_location + file
            with pdfplumber.open(full_path) as pdf:
                pages = pdf.pages[2:]
                raw_text = ''
                for page in pages:
                    raw_text += page.extract_text()
                split_raw_text = raw_text.split('\n')
                transactions = split_raw_text[7:len(split_raw_text)-7]
                # not good to hard code this come up with better way
                del transactions[39:46]
                for _, transaction in enumerate(transactions):
                    raw_transactions.append(
                        [transaction[:5], transaction[21:-6], transaction[transaction.rfind('£'):]])
            print(f"Collected data from {file}")

        formated_data = self.__format_transactional_data(raw_transactions)
        return self.__categorise_purchases(formated_data)

    def __format_transactional_data(self, data: List):
        """Function Docstring"""
        without_payments = [
            transaction for transaction in data if "FASTERPAYMENT" not in transaction[1]]

        without_balance = [
            transaction for transaction in without_payments if "Bal" not in transaction[0]]

        for idx, transaction in enumerate(without_balance):
            transaction[1] = transaction[1].rstrip()
            transaction[2] = float(
                transaction[2].replace('£', '').replace(',', ''))

            month = transaction[0][-3:]
            without_balance[idx][0] = transaction[0].replace(
                month, f'-{month_conversion.get(month)}-2021')
            transaction[0] = datetime.strptime(transaction[0], "%d-%m-%Y")

        final_data = without_balance

        return final_data

    def __categorise_purchases(self, data: List):
        """Function Docstring"""
        for transaction in data:
            for k, _ in category_conversion.items():
                if k in transaction[1].lower():
                    transaction.append(category_conversion[k])
                    break
            if len(transaction) == 3:
                transaction.append('other')
        return data

    def upload_to_mysql(self, data: List):
        """Function docstring"""
        if self.is_mysql:
            db_user = self.sql_settings.get('user')
            db_pwd = self.sql_settings.get('password')
            db_host = self.sql_settings.get('host')
            db_port = self.sql_settings.get('port')
            db_name = self.sql_settings.get('database')

            connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'

            engine = db.create_engine(connection_str)
            connection = engine.connect()

            for _, transaction in enumerate(data):
                sql = f"""
                    INSERT INTO {self.sql_settings['target_table']} 
                    (date, description, category, amount) 
                    VALUES ('{transaction[0]}', '{transaction[1]}', '{transaction[3]}', '{transaction[2]}');
                    """

                connection.execute(sql)

        print('Data has been successfully uploaded to MySQL')
