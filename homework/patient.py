import matplotlib.pyplot as plt
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property

import check as check
from loggers import my_logging_decorator
from db import Base, engine, session


class Patient(Base):
    __tablename__ = 'patients'

    _STATUSES = ("Болен", "Выздоровел", "Умер")

    @my_logging_decorator
    def __init__(self, first_name, last_name, birth_date, phone,
                 doc_type, doc_id, status="Болен", *, _with_check=True):
        if _with_check:
            attrs = check.global_check(first_name, last_name, birth_date,
                                       phone, doc_type, doc_id)

            self._first_name = attrs['first_name']
            self._last_name = attrs['last_name']
            self._birth_date = attrs['birth_date']
            self._phone = attrs['phone']
            self._document_type = attrs['doc_type']
            self._document_id = attrs['doc_id']
        else:
            self._first_name = first_name
            self._last_name = last_name
            self._birth_date = birth_date
            self._phone = phone
            self._document_type = doc_type
            self._document_id = doc_id

        if status in Patient._STATUSES:
            self._status = status
        else:
            raise ValueError

    @staticmethod
    def create(first_name, last_name, birth_date,
               phone, doc_type, doc_id, status="Болен"):
        return Patient(first_name, last_name, birth_date,
                       phone, doc_type, doc_id, status)

    def __str__(self):
        full_name = f"'{self._first_name} {self._last_name}',"
        full_name = "{:<23}".format(full_name)
        return f"[{full_name}{self._birth_date}, {self._phone}, " \
               f"{self._document_type}: " \
               f"{self._document_id}, Статус: {self._status}]"

    id = Column(Integer, primary_key=True)
    _first_name = Column("first_name", String, nullable=False)
    _last_name = Column("last_name", String, nullable=False)
    _birth_date = Column("birth_date", String, nullable=False)
    _phone = Column("phone", String, nullable=False)
    _document_type = Column("document_type", String, nullable=False)
    _document_id = Column("document_id", String, nullable=False)
    _status = Column("status", String, nullable=False)

    @hybrid_property
    def first_name(self):
        return self._first_name

    @hybrid_property
    def last_name(self):
        return self._last_name

    @hybrid_property
    def birth_date(self):
        return self._birth_date

    @hybrid_property
    def phone(self):
        return self._phone

    @hybrid_property
    def document_type(self):
        return self._document_type

    @hybrid_property
    def document_id(self):
        return self._document_id

    @my_logging_decorator
    @birth_date.setter
    def birth_date(self, new_date):
        new_date = check.check_birth_date(new_date)
        self._birth_date = new_date

    @my_logging_decorator
    @phone.setter
    def phone(self, new_phone):
        self._phone = new_phone

    @my_logging_decorator
    @document_type.setter
    def document_type(self, new_doc_type):
        new_doc_type = check.check_doc_type(new_doc_type)

        if new_doc_type is not self._document_type:
            self._document_type = new_doc_type
            self._document_id = NotImplemented
        else:
            raise ValueError("A mistake was made in document type")

    @my_logging_decorator
    @document_id.setter
    def document_id(self, new_id):
        new_id = check.check_doc_id(self._document_type, new_id)

        if self._document_id is NotImplemented:
            self._document_id = new_id
        elif check.is_typo_in_doc_id(self._document_id, new_id):
            self._document_id = new_id
        else:
            raise AttributeError("A typo is not found")

    def __eq__(self, other):
        if isinstance(other, Patient):
            return str(self) == str(other)
        else:
            raise ValueError

    @my_logging_decorator
    def recovered(self):
        self._status = "Выздоровел"

    @my_logging_decorator
    def dead(self):
        self._status = "Умер"

    @my_logging_decorator
    def save(self):
        session.add(self)
        session.commit()


Base.metadata.create_all(engine)


class PatientCollection:
    @my_logging_decorator
    def __init__(self, *, create_from_db=False):
        self._patients = []

        if create_from_db:
            self.create_from_db()

    @my_logging_decorator
    def add(self, first_name, last_name, date_of_birth,
            phone_number, doc_type, doc_number):

        new_patient = Patient(first_name, last_name, date_of_birth,
                              phone_number, doc_type, doc_number)

        self._patients.append(new_patient)
        new_patient.save()

    def __iter__(self):
        for one_patient in self._patients:
            yield one_patient

    @staticmethod
    def limit(last: int):
        for index, instance in enumerate(session.query(Patient).order_by(Patient.id)):
            if index < last:
                yield instance
            else:
                break

    def __len__(self):
        return len(self._patients)

    def update(self):
        self._patients = []
        self.create_from_db()

    @my_logging_decorator
    def create_from_db(self):
        for instance in session.query(Patient).order_by(Patient.id):
            self._patients.append(instance)

    @my_logging_decorator
    def get_statistical_chart(self):
        num_of_infected = 0
        num_of_recoveries = 0
        num_of_deaths = 0

        for patient in self:
            if patient._status == "Болен":
                num_of_infected += 1
            elif patient._status == "Выздоровел":
                num_of_recoveries += 1
            elif patient._status == "Умер":
                num_of_deaths += 1
            else:
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
