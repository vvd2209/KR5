# -*- coding: utf-8 -*-
from src.dbmanager import DBManager
from src.headhunter import HeadHunter
from config import JSON_FILE_NAME, employer_ids
from sql.db_queries import create_tables, insert_to_employers, insert_to_vacancies
from utils import user_interaction


def main():
    hh = HeadHunter()
    vacancies_list = hh.get_vacancies_by_api(employer_ids)  # получаем вакансии
    hh.save_vacancies_to_json(vacancies_list, JSON_FILE_NAME)  # записываем вакансии в файл

    while True:
        db_name = input('Введите слово на английском для названия базы данных: ')
        if all(one_letter in 'abcdefghijklmnopqrstuvwxyz1234567890' for one_letter in db_name):
            db = DBManager()
            break
        else:
            print("Введите слово на английском")
    db.create_database(db_name)  # создаём БД
    db.create_table(create_tables)  # создаём таблицы в БД
    db.insert_data_to_table(JSON_FILE_NAME, insert_to_employers, insert_to_vacancies)  # заполняем таблицы

    user_interaction(db)  # работаем с выборками в БД


if __name__ == '__main__':
    main()
