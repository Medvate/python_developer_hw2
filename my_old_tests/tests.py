import unittest
import os

from patient_collection import Patient, PatientCollection


class TestPatientMethods(unittest.TestCase):
    def test_init_1(self):
        example = Patient("Глеб", "Голубин", "1978---01---31", "+7 (949) 505-22-56",
                          "pfuhfybxysq gfcgjhn", "78[1581258]")

        self.assertEqual(example._first_name, "Глеб")
        self.assertEqual(example._last_name, "Голубин")
        self.assertEqual(example._birth_date, "1978-01-31")
        self.assertEqual(example._phone, "+7(949)505-22-56")
        self.assertTrue(example._document[0])  # It's "Загран. паспорт"
        self.assertEqual(example._document[1], "78 1581258")

    def test_init_2(self):
        example = Patient("Тамби", "Масаев", "1952.02.27", "8(940)246-24-11",
                          "загранчик", "(71)  5874634")

        self.assertEqual(example._first_name, "Тамби")
        self.assertEqual(example._last_name, "Масаев")
        self.assertEqual(example._birth_date, "1952-02-27")
        self.assertEqual(example._phone, "+7(940)246-24-11")
        self.assertTrue(example._document[0])  # It's "Загран. паспорт"
        self.assertEqual(example._document[1], "71 5874634")

    def test_init_3(self):
        example = Patient("Дмитрий", "Кузнецов", "1993/05/17",
                          "79421021995", "djl/ghdf", "3703833248")

        self.assertEqual(example._first_name, "Дмитрий")
        self.assertEqual(example._last_name, "Кузнецов")
        self.assertEqual(example._birth_date, "1993-05-17")
        self.assertEqual(example._phone, "+7(942)102-19-95")
        self.assertFalse(example._document[0])  # It's "Водительское удостоверение"
        self.assertEqual(example._document[1], "37 03 833248")

    def test_init_4(self):
        example = Patient("Прохор", "Шаляпин", "1970//07//30", "+8(950)(298)64)59)",
                          "ПАСПОРТ РФ", "(3752)(462732)")

        self.assertEqual(example._first_name, "Прохор")
        self.assertEqual(example._last_name, "Шаляпин")
        self.assertEqual(example._birth_date, "1970-07-30")
        self.assertEqual(example._phone, "+7(950)298-64-59")
        self.assertIsNone(example._document[0])  # It's "Паспорт РФ"
        self.assertEqual(example._document[1], "37 52 462732")

    def test_init_5(self):
        example = Patient("Федор", "Овальный", "1978-09-11", "+7915556-41-62",
                          "права водителя", "74 14 292010")

        self.assertEqual(example._first_name, "Федор")
        self.assertEqual(example._last_name, "Овальный")
        self.assertEqual(example._birth_date, "1978-09-11")
        self.assertEqual(example._phone, "+7(915)556-41-62")
        self.assertFalse(example._document[0])  # It's "Водительское удостоверение"
        self.assertEqual(example._document[1], "74 14 292010")

    def test_init_6(self):
        example = Patient("Александра", "Бортич", "1985..12..09",
                          "+7(937)5338516", "пАсПордик ФР", "4507[691152]")

        self.assertEqual(example._first_name, "Александра")
        self.assertEqual(example._last_name, "Бортич")
        self.assertEqual(example._birth_date, "1985-12-09")
        self.assertEqual(example._phone, "+7(937)533-85-16")
        self.assertIsNone(example._document[0])  # It's "Паспорт РФ"
        self.assertEqual(example._document[1], "45 07 691152")

    def test_create(self):
        human_1 = Patient("Иванушка", "Иванович", "1978-01-31", "89495052256",
                          "паспорт", "4814326902")

        human_2 = Patient.create("Иванушка", "Иванович", "1978-01-31", "89495052256",
                                 "паспорт", "4814326902")

        self.assertEqual(human_1, human_2)

    def test_to_str(self):
        example = Patient("Иванушка", "Иванович", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        answer = "['Иванушка Иванович',   1978-01-31, +7(949)505-22-56, Паспорт РФ: 48 14 326902]"

        self.assertEqual(str(example), answer)

    def test_getters(self):
        example = Patient("Иванушка", "Иванович", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.first_name, "Иванушка")
        self.assertEqual(example.last_name, "Иванович")
        self.assertEqual(example.birth_date, "1978-01-31")
        self.assertEqual(example.phone, "+7(949)505-22-56")
        self.assertEqual(example.document_type, "Паспорт РФ")
        self.assertEqual(example.document_id, "48 14 326902")

    def test_first_name_setter(self):
        # Мы можем изменять имя только в случае опечатки.
        example = Patient("Ивон", "Иванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.first_name, "Ивон")

        example.first_name = "Иван"
        self.assertEqual(example.first_name, "Иван")

        with self.assertRaises(AttributeError):
            example.first_name = "Влад"

    def test_last_name_setter(self):
        # Мы можем изменять фамилию только в случае опечатки.
        example = Patient("Иван", "Ыванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.last_name, "Ыванов")

        example.last_name = "Иванов"
        self.assertEqual(example.last_name, "Иванов")

        with self.assertRaises(AttributeError):
            example.last_name = "Антонов"

    def test_birth_date_setter(self):
        # Мы можем изменять дату рождения только в случае опечатки.
        example = Patient("Иван", "Иванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.birth_date, "1978-01-31")

        example.birth_date = "1978-10-31"
        self.assertEqual(example.birth_date, "1978-10-31")

        with self.assertRaises(AttributeError):
            example.birth_date = "1954.07.31"

    def test_phone_setter(self):
        # Мы можем изменять номер телефона в любом случае.
        example = Patient("Иван", "Иванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.phone, "+7(949)505-22-56")

        example.phone = "8[915]556_41_62"
        self.assertEqual(example.phone, "+7(915)556-41-62")

    def test_document_type_setter(self):
        # Мы можем изменять тип документа (и стереть тем самым его номер).
        example = Patient("Иван", "Иванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.document_type, "Паспорт РФ")
        self.assertEqual(example.document_id, "48 14 326902")

        example.document_type = "пэспортос"
        self.assertEqual(example.document_type, "Паспорт РФ")
        self.assertEqual(example.document_id, "48 14 326902")

        example.document_type = "права"
        self.assertEqual(example.document_type, "Водительские права")
        self.assertIs(example.document_id, NotImplemented)

    def test_document_id_setter(self):
        # Мы можем изменить номер документа,
        # если в нем была опечатка, или если мы
        # перед этим изменили тип документа.
        example = Patient("Иван", "Иванов", "1978-01-31",
                          "89495052256", "паспорт", "4814326902")

        self.assertEqual(example.document_type, "Паспорт РФ")
        self.assertEqual(example.document_id, "48 14 326902")

        with self.assertRaises(AttributeError):
            example.document_id = "4612749681"

        example.document_id = "4914326903"

        self.assertEqual(example.document_type, "Паспорт РФ")
        self.assertEqual(example.document_id, "49 14 326903")

        example.document_type = "права"
        self.assertEqual(example.document_type, "Водительские права")
        self.assertIs(example.document_id, NotImplemented)

        example.document_id = "4612749681"
        self.assertEqual(example.document_id, "46 12 749681")


class TestPatientCollectionMethods(unittest.TestCase):
    def test_init(self):
        collection = PatientCollection()

        self.assertFalse(len(collection))

    def test_init_from_empty_file(self):
        with self.assertRaises(FileNotFoundError):
            collection = PatientCollection("nonexistent.csv")

        open("new_file.csv", 'w').close()

        collection = PatientCollection("new_file.csv")
        self.assertFalse(len(collection))

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'new_file.csv')
        os.remove(path)

    def test_add(self):
        first_names = ["Глеб", "Тамби", "Дмитрий", "Прохор", "Федор", "Александра"]
        last_names = ["Голубин", "Масаев", "Кузнецов", "Шаляпин", "Овальный", "Бортич"]
        birth_dates = ["1978-01-31", "1952-02-27", "1993-05-17",
                       "1970-07-30", "1978-09-11", "1985-12-09"]
        phone = ["+7(949)505-22-56", "+7(940)246-24-11", "+7(942)102-19-95",
                 "+7(950)298-64-59", "+7(915)556-41-62", "+7(937)533-85-16"]
        doc_types = ["Водительские права", "Загран. паспорт", "Паспорт РФ",
                     "Паспорт РФ", "Водительские права", "Загран. паспорт"]
        doc_ids = ["78 15 812581", "71 5874634", "37 03 833248",
                   "37 52 462732", "74 14 292010", "45 0769112"]

        collection = PatientCollection()

        for i in range(6):
            collection.add(first_names[i], last_names[i], birth_dates[i],
                           phone[i], doc_types[i], doc_ids[i])

        for index, one_patient in enumerate(collection):
            self.assertEqual(one_patient.first_name, first_names[index])
            self.assertEqual(one_patient.last_name, last_names[index])
            self.assertEqual(one_patient.birth_date, birth_dates[index])
            self.assertEqual(one_patient.phone, phone[index])
            self.assertEqual(one_patient.document_type, doc_types[index])
            self.assertEqual(one_patient.document_id, doc_ids[index])

    def test_save(self):
        first_names = ["Глеб", "Тамби", "Дмитрий", "Прохор", "Федор", "Александра"]
        last_names = ["Голубин", "Масаев", "Кузнецов", "Шаляпин", "Овальный", "Бортич"]
        birth_dates = ["1978-01-31", "1952-02-27", "1993-05-17",
                       "1970-07-30", "1978-09-11", "1985-12-09"]
        phone = ["+7(949)505-22-56", "+7(940)246-24-11", "+7(942)102-19-95",
                 "+7(950)298-64-59", "+7(915)556-41-62", "+7(937)533-85-16"]
        doc_types = ["Водительские права", "Загран. паспорт", "Паспорт РФ",
                     "Паспорт РФ", "Водительские права", "Загран. паспорт"]
        doc_ids = ["78 15 812581", "71 5874634", "37 03 833248",
                   "37 52 462732", "74 14 292010", "45 0769112"]

        collection_1 = PatientCollection()

        for i in range(6):
            collection_1.add(first_names[i], last_names[i], birth_dates[i],
                             phone[i], doc_types[i], doc_ids[i])

        collection_1.save("new_file.csv")

        collection_2 = PatientCollection("new_file.csv")

        for first_patient, second_patient in zip(collection_1, collection_2):
            self.assertEqual(first_patient, second_patient)

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "new_file.csv")
        os.remove(path)


if __name__ == '__main__':
    unittest.main()

