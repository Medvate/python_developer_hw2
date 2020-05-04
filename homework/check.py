import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import fuzz, process

from homework.loggers import INFO_LOG, ERR_LOG


def check_first_name(first_name):
    if isinstance(first_name, str):
        if first_name.isalpha():
            first_name = first_name.capitalize()

            page = requests.get(f"http://imenator.ru/search/?text={first_name}")
            soup = BeautifulSoup(page.content, "html.parser")
            all_links = soup.find_all(name='a')

            for link in all_links:
                if link.text == first_name:
                    # Commented to pass the tests.
                    # INFO_LOG.info(f"Имя '{first_name}' было найдено в БД!")
                    return first_name
            else:
                INFO_LOG.warning(f"Имя '{first_name}' не было найдено в БД!")
                return first_name
        else:
            ERR_LOG.error(f"Ошибка в 'имени': '{first_name}'")
            raise ValueError("The first name contains invalid characters")
    else:
        ERR_LOG.error(f"Ошибка в 'имени': '{first_name}'")
        raise TypeError("A mistake was made in the first name")


def check_last_name(last_name):
    if isinstance(last_name, str):
        if last_name.isalpha():
            last_name = last_name.capitalize()

            page = requests.get(f"http://www.ufolog.ru/names/order/{last_name.lower()}")

            soup = BeautifulSoup(page.content, "html.parser")
            found = soup.find_all(name='span', attrs={'class': 'version-number'})

            if found:
                # Commented to pass the tests.
                # INFO_LOG.info(f"Фамилия '{last_name}' была найдена в БД!")
                pass
            else:
                INFO_LOG.warning(f"Фамилия '{last_name}' не была найдена в БД!")

            return last_name
        else:
            ERR_LOG.error(f"Ошибка в 'фамилии': '{last_name}'")
            raise ValueError("The last name contains invalid characters")
    else:
        ERR_LOG.error(f"Ошибка в 'фамилии': '{last_name}'")
        raise TypeError("A mistake was made in the last name")


def check_birth_date(birth_date):
    if isinstance(birth_date, str):
        if not any(symbol.isalpha() for symbol in birth_date):
            result = str(pd.to_datetime(birth_date).date())
            return result
        else:
            ERR_LOG.error(f"Ошибка в 'дате рождения': '{birth_date}'")
            raise ValueError("Invalid Date of Birth")
    else:
        ERR_LOG.error(f"Ошибка в 'дате рождения': '{birth_date}'")
        raise TypeError("A mistake was made in the Date of Birth")


def convert_phone_number(num: str):
    if len(num) == 11:
        return f"+7({num[1:4]}){num[4:7]}-{num[7:9]}-{num[9:11]}"
    else:
        ERR_LOG.error(f"Ошибка в 'номере телефона': '{num}'")
        raise ValueError("Invalid phone number")


def check_phone(phone):
    if not isinstance(phone, str):
        if 10_000_000_000 <= phone <= 99_999_999_999:
            phone = str(phone)
        else:
            ERR_LOG.error(f"Ошибка в 'номере телефона': '{phone}'")
            raise TypeError("A mistake was made in the phone number")

    phone = ''.join(filter(str.isdigit, phone))
    return convert_phone_number(phone)


def get_good_doc_type(bad_doc_type):
    if "заграничный" in bad_doc_type:
        return True
    elif "паспорт" in bad_doc_type:
        return None
    else:
        return False


def check_doc_type(doc_type):
    if isinstance(doc_type, str):
        doc_type = doc_type.lower()
        variants = ["паспорт российский", "заграничный паспорт",
                    "водительское удостоверение, права"]

        result = process.extractOne(doc_type, variants)

        if result[1] < 40:
            doc_type = eng_to_rus(doc_type)
            result = process.extractOne(doc_type, variants)
            if result[1] < 40:
                ERR_LOG.error(f"Низкий показатель: {result[1]}% (Тип документа: '{doc_type}')")
                raise ValueError("Invalid doc type")
        elif result[1] < 60:
            INFO_LOG.warning(f"Низкий показатель: {result[1]}% (Тип документа: '{doc_type}')")

        return get_good_doc_type(result[0])
    else:
        ERR_LOG.error(f"Ошибка в doc_type: '{doc_type}'")
        raise TypeError("A mistake was made in the doc type")


def check_doc_id(doc_type, doc_id):
    if isinstance(doc_id, str):
        doc_id = ''.join(filter(str.isdigit, doc_id))

        if doc_type and len(doc_id) == 9:
            return f"{doc_id[:2]} {doc_id[2:]}"
        elif doc_type is None and len(doc_id) == 10:
            return f"{doc_id[:4]} {doc_id[4:]}"
        elif not doc_type and len(doc_id) == 10:
            return f"{doc_id[:2]} {doc_id[2:4]} {doc_id[4:]}"
        else:
            ERR_LOG.error(f"Ошибка в 'номере документа': '{doc_id}'")
            raise ValueError("Invalid doc id")

    ERR_LOG.error(f"Ошибка в doc_id: '{doc_id}'")
    raise TypeError("A mistake was made in doc number")


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


def is_typo_in_name(old_name, new_name):
    percent = fuzz.partial_ratio(old_name, new_name)

    if not percent:
        new_name = eng_to_rus(new_name)
        percent = fuzz.partial_ratio(old_name, new_name)

    return percent > 59


def is_typo_in_date(old_date, new_date):
    percent = fuzz.partial_ratio(old_date, new_date)
    return percent > 81


def is_typo_in_doc_id(old_id, new_id):
    percent = fuzz.partial_ratio(old_id, new_id)
    return percent > 79
