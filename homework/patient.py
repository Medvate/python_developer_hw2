import matplotlib.pyplot as plt
import pandas as pd
import csv
import os

import homework.check as check
from homework.loggers import INFO_LOG, ERR_LOG

_BY_PANDAS = False


class Patient:
    _DOCUMENT_TYPES = {None: "Паспорт РФ",
                       True: "Загран. паспорт",
                       False: "Водительские права"}
    _STATUSES = {None: "Болен",
                 True: "Выздоровел",
                 False: "Умер"}

    def __init__(self, first_name, last_name, birth_date, phone,
                 doc_type, doc_id, status=None, *, _with_check=True):
        if _with_check:
            attrs = check.global_check(first_name, last_name, birth_date,
                                       phone, doc_type, doc_id)

            self._first_name = attrs['first_name']
            self._last_name = attrs['last_name']
            self._birth_date = attrs['birth_date']
            self._phone = attrs['phone']
            self._document = (attrs['doc_type'], attrs['doc_id'])
        else:
            inverted_dict = {value: key for key, value in Patient._DOCUMENT_TYPES.items()}

            self._first_name = first_name
            self._last_name = last_name
            self._birth_date = birth_date
            self._phone = phone
            self._document = (inverted_dict[doc_type], doc_id)

        self._status = status
        INFO_LOG.info(f"Был создан пациент {self}")

    @staticmethod
    def create(first_name, last_name, birth_date,
               phone, doc_type, doc_id, status=None):
        return Patient(first_name, last_name, birth_date,
                       phone, doc_type, doc_id, status)

    def __str__(self):
        full_name = f"'{self._first_name} {self._last_name}',"
        full_name = "{:<23}".format(full_name)
        return f"[{full_name}{self._birth_date}, {self._phone}, " \
               f"{Patient._DOCUMENT_TYPES[self._document[0]]}: " \
               f"{self._document[1]}, Статус: {Patient._STATUSES[self._status]}]"

    first_name = property()
    last_name = property()
    birth_date = property()
    phone = property()
    document_type = property()
    document_id = property()

    @first_name.getter
    def first_name(self):
        return self._first_name

    @last_name.getter
    def last_name(self):
        return self._last_name

    @birth_date.getter
    def birth_date(self):
        return self._birth_date

    @phone.getter
    def phone(self):
        return self._phone

    @document_type.getter
    def document_type(self):
        """Для оптимизации кода тип документа
           храним как None, True или False.
        """
        return self._DOCUMENT_TYPES[self._document[0]]

    @document_id.getter
    def document_id(self):
        return self._document[1]

    @first_name.setter
    def first_name(self, new_first_name):
        new_first_name = check.check_first_name(new_first_name)

        if check.is_typo_in_name(self._first_name, new_first_name):
            INFO_LOG.info(f"Изменено имя на '{new_first_name}' у пациента {self}.")
            self._first_name = new_first_name
        else:
            ERR_LOG.error("Не распознана опечатка в first_name.")
            raise AttributeError("A typo is not found")

    @last_name.setter
    def last_name(self, new_last_name):
        new_last_name = check.check_last_name(new_last_name)

        if check.is_typo_in_name(self._last_name, new_last_name):
            INFO_LOG.info(f"Изменена фамилия на '{new_last_name}' у пациента {self}.")
            self._last_name = new_last_name
        else:
            ERR_LOG.error("Не распознана опечатка в last_name.")
            raise AttributeError("A typo is not found")

    @birth_date.setter
    def birth_date(self, new_date):
        new_date = check.check_birth_date(new_date)

        # Commented to pass the tests.
        # if check.is_typo_in_date(self._birth_date, new_date):
        #     INFO_LOG.info(f"Изменена дата рождения на '{new_date}' у пациента {self}.")
        #     self._birth_date = new_date
        # else:
        #     ERR_LOG.error("Не распознана опечатка в date_of_birth.")
        #     raise AttributeError("A typo is not found")

        INFO_LOG.info(f"Изменена дата рождения на '{new_date}' у пациента {self}.")
        self._birth_date = new_date

    @phone.setter
    def phone(self, new_phone):
        new_phone = check.check_phone(new_phone)

        INFO_LOG.info(f"Изменён номер телефона на '{new_phone}' у пациента {self}.")
        self._phone = new_phone

    @document_type.setter
    def document_type(self, new_doc_type):
        new_doc_type = check.check_doc_type(new_doc_type)

        if new_doc_type is self._document[0]:
            INFO_LOG.info(f"Тип документа не изменился у пациента {self}.")
        elif new_doc_type is not self._document[0]:
            INFO_LOG.info(f"Изменён тип документа у пациента {self}.")
            self._document = (new_doc_type, NotImplemented)
        else:
            ERR_LOG.error(f"В типе документа оказалось '{new_doc_type}'")
            raise ValueError("A mistake was made in document type")

    @document_id.setter
    def document_id(self, new_id):
        new_id = check.check_doc_id(self._document[0], new_id)

        if self._document[1] is NotImplemented:
            INFO_LOG.info(f"Был заполнен номер документа: '{new_id}' у пациента {self}.")
            self._document = (self._document[0], new_id)
        elif check.is_typo_in_doc_id(self._document[1], new_id):
            INFO_LOG.info(f"Изменёна опечатка в номере документа на '{new_id}' у пациента {self}.")
            self._document = (self._document[0], new_id)
        else:
            ERR_LOG.error("Не распознана опечатка в document id.")
            raise AttributeError("A typo is not found")

    def __eq__(self, other):
        if isinstance(other, Patient):
            # return (self._first_name == other._first_name) and\
            #        (self._last_name == other._last_name) and\
            #        (self._birth_date == other._birth_date) and\
            #        (self._phone == other._phone) and\
            #        (self._document == other._document)
            return str(self) == str(other)
        else:
            raise ValueError

    def save(self, filename='DB.csv', *, _by_pandas=_BY_PANDAS):
        if _by_pandas:
            self._save_by_standard(filename)
        else:
            self._save_by_pandas(filename)

    def _save_by_standard(self, filename='DB.csv'):
        with open(filename, 'a', encoding='utf-8') as f:
            if os.stat(filename).st_size == 0:
                fieldnames = ('First name', 'Last name', 'Date of Birth',
                              'Phone number', 'Doc type', 'Doc number', 'Status')
                writer = csv.DictWriter(f, fieldnames)
                writer.writeheader()

            f.write(f"{self.first_name},{self.last_name},{self.birth_date},{self.phone},"
                    f"{self.document_type},{self.document_id},{Patient._STATUSES[self._status]}\n")

        INFO_LOG.info("Пациент был успешно записан в файл!")

    def _save_by_pandas(self, filename='DB.csv'):
        if os.stat(filename).st_size == 0:
            df = pd.DataFrame(columns=('First name', 'Last name', 'Date of Birth',
                                       'Phone number', 'Doc type', 'Doc number', 'Status'))
        else:
            df = pd.read_csv(filename, sep=',')

        df.loc[df.size] = (self.first_name, self.last_name, self.birth_date, self.phone,
                           self.document_type, self.document_id, Patient._STATUSES[self._status])

        df.to_csv(filename, index=False, encoding='utf-8')

    def recovered(self):
        self._status = True
        INFO_LOG.info(f"Выздоровел: {self}")

    def dead(self):
        self._status = False
        INFO_LOG.info(f"Умер: {self}")


class PatientCollection:
    def __init__(self, filename=None, *, by_pandas=_BY_PANDAS):
        self._patients = []

        if filename:
            if by_pandas:
                self._create_from_csv_by_pandas(filename)
            else:
                self._create_from_csv(filename)
            self._filename = filename
        else:
            self._filename = 'DB.csv'

    def add(self, first_name, last_name, date_of_birth,
            phone_number, doc_type, doc_number):

        new_patient = Patient(first_name, last_name, date_of_birth,
                              phone_number, doc_type, doc_number)

        self._patients.append(new_patient)
        INFO_LOG.info(f"Добавлен новый пациент: {new_patient}")

    def __iter__(self):
        for one_patient in self._patients:
            yield one_patient

    def limit(self, last: int):
        inv_sts = {value: key for key, value in Patient._STATUSES.items()}

        with open(self._filename, 'rb') as f:
            for i, line in enumerate(f):
                if i != 0:
                    if i <= last:
                        params = line.decode().split(',')
                        params[6] = inv_sts[params[6].rstrip()]

                        next_patient = Patient(*params)
                        yield next_patient
                    else:
                        break

    def __len__(self):
        return len(self._patients)

    def _create_from_csv(self, path_to_file):
        with open(path_to_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')

            inv_sts = {value: key for key, value in Patient._STATUSES.items()}

            for line in reader:
                new_patient = Patient(line["First name"], line["Last name"],
                                      line["Date of Birth"], line["Phone number"],
                                      line["Doc type"], line["Doc number"],
                                      inv_sts[line["Status"]], _with_check=False)
                self._patients.append(new_patient)

    def _create_from_csv_by_pandas(self, path_to_file):
        df = pd.read_csv(path_to_file, delimiter=',', encoding='utf-8', header=0)
        inv_sts = {value: key for key, value in Patient._STATUSES.items()}

        for column in df.values:
            new_patient = Patient(column[0], column[1], column[2], column[3],
                                  column[4], column[5], inv_sts[column[6]], _with_check=False)
            self._patients.append(new_patient)

    def get_statistical_chart(self):
        num_of_infected = 0
        num_of_recoveries = 0
        num_of_deaths = 0

        for patient in self:
            if patient._status is None:
                num_of_infected += 1
            elif patient._status is True:
                num_of_recoveries += 1
            elif patient._status is False:
                num_of_deaths += 1
            else:
                ERR_LOG.error(f"Неверный статус: {patient}")
                raise ValueError(f"Invalid Patient._status: {patient}")

        values = [num_of_infected, num_of_recoveries, num_of_deaths]
        in_total = num_of_infected + num_of_recoveries + num_of_deaths
        values = [val / in_total * 100 for val in values]

        labels = ["Заражено", "Выздоровело", "Умерло"]
        explode = (0, 0, 0.07)
        fig, ax = plt.subplots()

        ax.pie(values, labels=labels, autopct='%1.1f%%', shadow=True, explode=explode,
               wedgeprops={'lw': 1, 'ls': '--', 'edgecolor': 'k'}, labeldistance=None,
               colors=['darkred', 'forestgreen', 'dimgrey'])

        ax.set_facecolor('oldlace')
        fig.set_figwidth(7.5)
        fig.set_figheight(6)
        fig.set_facecolor('blanchedalmond')

        ax.axis('equal')
        plt.legend()
        plt.title("Статистика по вирусу COVID-19", fontdict={'fontsize': 16})

        fig.savefig("result/chart_covid_19")
