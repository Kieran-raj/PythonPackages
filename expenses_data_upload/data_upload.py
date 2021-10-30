"""Module to upload pdf statements"""
import os
from typing import List

import pdfplumber

from expenses_data_upload.helpers.mappings import category_conversion, month_conversion

class PdfScanner():
    """Class Docstring"""
    def __init__(self, file_location: str):
        self.file_location = file_location

    def get_raw_transactions(self):
        """Function Docstring"""
        raw_transactions =[]
        for file in os.listdir(self.file_location ):
            full_path = self.file_location  + file
            with pdfplumber.open(full_path) as pdf:
                pages = pdf.pages[2:]
                raw_text = ''
                for page in pages:
                    raw_text += page.extract_text()
                split_raw_text = raw_text.split('\n')
                transactions = split_raw_text[7:len(split_raw_text)-6]
                del transactions[39:46] # not good to hard code this come up with better way
                for idx, transaction in enumerate(transactions):
                    if '-£' in transaction:
                        transactions.pop(idx)
                    raw_transactions.append([transaction[:5], transaction[21:-6], transaction[transaction.rfind('£'):]])

        formated_data = self.format_transactional_data(raw_transactions)
        return self.categorise_purchases(formated_data)


    def format_transactional_data(self, data: List):
        """Function Docstring"""
        for i, transaction in enumerate(data):
            transaction[1] = transaction[1].rstrip()
            transaction[2] = float(transaction[2].replace('£', ''))

            month = transaction[0][-3:]
            data[i][0] = transaction[0].replace(month, f'-{month_conversion[month]}-2021')

        return data

   
    def categorise_purchases(self, data: List):
        """Function Docstring"""
        for transaction in data:
            for k, v in category_conversion.items():
                if k in transaction[1].lower():
                    transaction.append(category_conversion[k])
                    break
                if len(transaction) == 3:
                    transaction.append('other')
        return data
