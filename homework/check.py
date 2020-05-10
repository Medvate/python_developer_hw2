import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import fuzz, process

from loggers import my_logging_decorator


FIRST_NAME_URL = "http://imenator.ru/search/?text="
LAST_NAME_URL = "http://www.ufolog.ru/names/order/"


@my_logging_decorator
def check_first_name(first_name):
    if not isinstance(first_name, str):
        raise TypeError("A mistake was made in the first name")

    if first_name.isalpha():
        first_name = first_name.capitalize()

        page = requests.get(FIRST_NAME_URL + first_name)
        soup = BeautifulSoup(page.content, "html.parser")
        all_links = soup.find_all(name='a')

        for link in all_links:
            if link.text == first_name:
                return first_name
        else:
            raise ValueError("Invalid first name")
    else:
        raise ValueError("The first name contains invalid characters")


@my_logging_decorator
def check_last_name(last_name):
    if not isinstance(last_name, str):
        raise TypeError("A mistake was made in the last name")

    if last_name.isalpha():
        last_name = last_name.capitalize()

        page = requests.get(LAST_NAME_URL + last_name.lower())

        soup = BeautifulSoup(page.content, "html.parser")
        found = soup.find_all(name='span', attrs={'class': 'version-number'})

        if found:
            return last_name
        else:
            raise ValueError("Invalid last name")
    else:
        raise ValueError("The last name contains invalid characters")


@my_logging_decorator
def check_birth_date(birth_date):
    if not isinstance(birth_date, str):
        raise TypeError("A mistake was made in the Date of Birth")

    if not any(symbol.isalpha() for symbol in birth_date):
        result = str(pd.to_datetime(birth_date).date())
        return result
    else:
        raise ValueError("Invalid Date of Birth")


@my_logging_decorator
def convert_phone_number(num: str):
    if len(num) == 11:
        return f"+7({num[1:4]}){num[4:7]}-{num[7:9]}-{num[9:11]}"
    else:
        raise ValueError("Invalid phone number")


@my_logging_decorator
def check_phone(phone):
    if not isinstance(phone, str):
        if 10_000_000_000 <= phone <= 99_999_999_999:
            phone = str(phone)
        else:
            raise TypeError("A mistake was made in the phone number")

    phone = ''.join(filter(str.isdigit, phone))
    return convert_phone_number(phone)


def get_good_doc_type(bad_doc_type):
    if "заграничный" in bad_doc_type:
        return "Загран. паспорт"
    elif "паспорт" in bad_doc_type:
        return "Паспорт РФ"
    else:
        return "Водительские права"


@my_logging_decorator
def check_doc_type(doc_type):
    if not isinstance(doc_type, str):
        raise TypeError("A mistake was made in the document type")

    doc_type = doc_type.lower()
    variants = ["паспорт российский", "заграничный паспорт",
                "водительское удостоверение, права"]

    result = process.extractOne(doc_type, variants)

    if result[1] < 40:
        doc_type = eng_to_rus(doc_type)
        result = process.extractOne(doc_type, variants)
        if result[1] < 40:
            raise ValueError("Invalid document type")

    return get_good_doc_type(result[0])


@my_logging_decorator
def check_doc_id(doc_type, doc_id):
    if not isinstance(doc_id, str):
        raise TypeError("A mistake was made in document ID")

    doc_id = ''.join(filter(str.isdigit, doc_id))

    if (doc_type == "Загран. паспорт") and (len(doc_id) == 9):
        return f"{doc_id[:2]} {doc_id[2:]}"
    elif (doc_type == "Паспорт РФ") and (len(doc_id) == 10):
        return f"{doc_id[:4]} {doc_id[4:]}"
    elif (doc_type == "Водительские права") and (len(doc_id) == 10):
        return f"{doc_id[:2]} {doc_id[2:4]} {doc_id[4:]}"
    else:
        raise ValueError("Invalid document ID")




def global_check(first_name, last_name, birth_date,
                 phone, doc_type, doc_id):
    result = dict()

    result['first_name'] = check_first_name(first_name)
    result['last_name'] = check_last_name(last_name)
    result['birth_date'] = check_birth_date(birth_date)
    result['phone'] = check_phone(phone)
    result['doc_type'] = check_doc_type(doc_type)
    result['doc_id'] = check_doc_id(result['doc_type'], doc_id)

    return result


def eng_to_rus(string):
    layout = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                               'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'),
                               "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                               'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'))

    return string.translate(layout)


def is_typo_in_doc_id(old_id, new_id):
    percent = fuzz.partial_ratio(old_id, new_id)
    return percent > 79
