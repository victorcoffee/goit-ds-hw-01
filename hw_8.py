# Модуль 1.

import os, re, datetime
from collections import UserDict
import pickle

os.system("cls")


# Декоратор обробляє винятки, що виникають у функціях
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return "Address Book File is not found"
        except KeyError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command IndexError"
        except ValueError:
            return "Enter the argument for the command ValueError"

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    pass


class Phone(Field):
    # Перевірка номера на коректність - 10 цифр
    def __init__(self, value):
        pattern = r"\d{10}"
        match = re.search(pattern, str(value))
        if match:
            super().__init__(value)
        else:
            # print("Invalid number, must be 10 digits")
            raise ValueError("Invalid number")


class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевірка коректності дати
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Додавання телефону до контакту
    def add_phone(self, phone: Phone):
        try:
            phone = Phone(phone)
            self.phones.append(phone)
            print(f"Number {phone} added for {self.name.value}")
        except ValueError:
            print("Invalid number, must be 10 digits")

    # Видалення телефону до контакту. В данному релізі не використовується
    def remove_phone(self, phone: Phone):
        phone = Phone(phone)
        for index in range(len(self.phones)):
            if phone.value == self.phones[index].value:
                print(f"Number {phone.value} deleted for {self.name.value}")
                del self.phones[index]
                return
        else:
            print(f"Phone {phone.value} not found - remove_phone")

    # Редагування телефону для контакту
    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        old_phone = Phone(old_phone)
        new_phone = Phone(new_phone)
        for index in range(len(self.phones)):
            if old_phone.value == self.phones[index].value:
                self.phones[index] = new_phone
                return f"Number {new_phone.value} updated for {self.name.value}"
        else:
            return f"Phone {old_phone.value} not found - edit_phone"

    # Додавання дня народження до контакту
    def _add_birthday(self, date: str):
        try:
            birthday = Birthday(date)
            self.birthday = birthday
            print(f"Birthday {date} added for {self.name.value}")
        except Exception as e:
            print("Invalid date format. Use DD.MM.YYYY")

    # Формат виведення контакту
    def __str__(self):
        result = f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        if self.birthday:
            result += "; birthday: " + self.birthday.value.strftime("%d.%m.%Y")
        return result


class AddressBook(UserDict):
    book = UserDict()

    # Додавання контакту до книги
    def add_record(self, record: Record):
        self.data[record.name] = record

    # Пошук контакту
    def find(self, name: Name) -> Record:
        for key, value in self.data.items():
            if key.value == name:
                return self.data[key]
        return

    # Видалення контакту з книги. В даному релізі не використовується
    def delete(self, name: Name):
        for key, value in self.data.items():
            if key.value == name:
                print(f"{self.data[key]} deleted")
                del self.data[key]
                break
        else:
            print("Contact {name} is absent")

    # Функція повертає список іменинників на найближчі 7 днів
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.datetime.today().date()
        end_week = today + datetime.timedelta(days=7)
        print("This week birthdays:")
        print("Name        Born       Birthday   Congratulate")
        for key, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_this_year = datetime.date(
                    today.year, birthday.month, birthday.day
                )

                # Якщо день народження вже був у цьому році, визначаємо наступний
                if birthday_this_year < today:
                    birthday_next_year = datetime.date(
                        today.year + 1, birthday.month, birthday.day
                    )
                    nearest_birthday = birthday_next_year
                else:
                    nearest_birthday = birthday_this_year

                # Перенесення привітання з вихідних  на понеділок
                if nearest_birthday.weekday() == 5:
                    congratulation_date = nearest_birthday + datetime.timedelta(days=2)
                elif nearest_birthday.weekday() == 6:
                    congratulation_date = nearest_birthday + datetime.timedelta(days=1)
                else:
                    congratulation_date = nearest_birthday

                # Якщо день народження у найближчі 7 днів, то додаємо у список
                if today <= nearest_birthday < end_week:
                    person_to_congratulate = {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                    bthday = birthday.strftime("%d.%m.%Y")
                    bthdaythis = birthday_this_year.strftime("%d.%m.%Y")
                    congrat = congratulation_date.strftime("%d.%m.%Y")
                    print(
                        f"{record.name.value:8} {bthday:12} {bthdaythis:12} {congrat:12}"
                    )
                    upcoming_birthdays.append(person_to_congratulate)

        return upcoming_birthdays


# Додавання дня народження для контакта
@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if birthday:
        record._add_birthday(birthday)
    return message


# Виведення інформації про день народження контакта
@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        message = "Contact not found."
    elif record.birthday:
        message = f"Contact name: {record.name.value}, birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    else:
        message = f"There is no any information about {record.name.value}'s birthday"
    print(message)


# Виведення найближчих днів народження
@input_error
def birthdays(args, book):
    book.get_upcoming_birthdays()


# Пошук контакта за іменем
@input_error
def phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        message = "Contact not found."
    elif record.phones:
        message = f"Contact name: {record.name.value}, phones: {'; '.join(p.value for p in record.phones)}"
    else:
        message = f"There is no any information about {record.name.value}'s phone"
    print(message)


# Парсер команд
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


# Додавання контакту.
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


# Зміна контакту
@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record:
        message = record.edit_phone(old_phone, new_phone)
        return message
    else:
        return "Contact was not updated"


#  Виведення всіх контаків
@input_error
def show_all(book: AddressBook):
    for name, record in book.data.items():
        print(record)
    print("All list of contacts printed.")
    return


# Збереження адресної книги у файл
@input_error
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


# Зчитування адресної книги з файлу
@input_error
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


# Основна програма
def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            phone(args, book)

        elif command == "all":
            show_all(book)

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(args, book)

        else:
            print("Invalid command.")

    save_data(book)


if __name__ == "__main__":
    main()
