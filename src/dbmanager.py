# -*- coding: utf-8 -*-
import psycopg2
import json
import os
from config import config, JSON_DATA_DIR


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self):
        self.database_name = None

    def connect_to_database(self):
        """Метод для подключения к базе данных"""
        params = config()
        return psycopg2.connect(dbname=self.database_name, **params)

    def create_database(self, dbname: str) -> None:
        """
        Метод для создания базы данных
        :param dbname: имя создаваемой базы данных
        """
        try:
            connection = self.connect_to_database()
            connection.autocommit = True
            # Создаём базу данных
            with connection.cursor() as cur:
                cur.execute(f'DROP DATABASE IF EXISTS {dbname}')
                cur.execute(f'CREATE DATABASE {dbname}')
                self.database_name = dbname
                print(f'База данных {dbname} успешно создана')

            connection.close()

        except psycopg2.OperationalError as e:
            print(f'Ошибка создания базы данных: {e}')

    def create_table(self, create_table_query: str) -> None:
        """
        Метод для создания таблиц в базе данных
        :param create_table_query: запрос для создания таблиц
        """
        try:
            with self.connect_to_database() as connection:
                # Создаём таблицы
                with connection.cursor() as cur:
                    cur.execute(create_table_query)
                    print('Таблицы успешно созданы')
            connection.commit()
            connection.close()

        except psycopg2.OperationalError as e:
            print(e)

    def insert_data_to_table(self, data_filename: str, employers_query: str, vacancies_query: str) -> None:
        """
        Метод для заполнения таблиц в базе данных из файла json
        :param data_filename: файл json с данными
        :param employers_query: запрос для заполнения таблицы работодателей
        :param vacancies_query: запрос для заполнения таблицы вакансий
        """
        # Читаем данные из файла
        filepath = os.path.join(JSON_DATA_DIR, data_filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Заполняем таблицы данными из файла
        try:
            with self.connect_to_database() as connection:
                connection.autocommit = True
                with connection.cursor() as cur:
                    for vacancy in data:
                        cur.execute(employers_query, (vacancy['employer'], vacancy['employer']))

                        cur.execute("SELECT employer_id FROM employers ORDER BY employer_id DESC LIMIT 1")
                        employer_id = cur.fetchone()

                        cur.execute(vacancies_query, (employer_id, vacancy['vacancy_title'],
                                                      vacancy['vacancy_url'], vacancy['vacancy_area'],
                                                      vacancy['salary_from'], vacancy['salary_to']))

                print(f'Таблицы успешно заполнены данными из файла {data_filename}')

            connection.close()

        except psycopg2.Error as e:
            print(f"Ошибка заполнения: {e}")

    def get_companies_and_vacancies_count(self, companies_and_vacancies_count_query: str):
        """Получает список всех компаний и количество вакансий у каждой компании"""
        with self.connect_to_database() as connection:
            with connection.cursor() as cur:
                cur.execute(companies_and_vacancies_count_query)
                res = cur.fetchall()
        connection.close()
        return res

    def get_all_vacancies(self, all_vacancies_query: str):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with self.connect_to_database() as connection:
            with connection.cursor() as cur:
                cur.execute(all_vacancies_query)
                res = cur.fetchall()
        connection.close()
        return res

    def get_avg_salary(self, avg_salary_query):
        """Получает среднюю зарплату по вакансиям"""
        query = "SELECT CAST(AVG((salary_from+salary_to)/2) AS INT) FROM vacancies"
        with self.connect_to_database() as connection:
            with connection.cursor() as cur:
                cur.execute(avg_salary_query)
                res = cur.fetchone()[0]
        connection.close()
        return res

    def get_vacancies_with_higher_salary(self, vacancies_with_higher_salary_query):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        with self.connect_to_database() as connection:
            with connection.cursor() as cur:
                cur.execute(vacancies_with_higher_salary_query)
                res = cur.fetchall()
        connection.close()
        return res

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        vacancies_with_keyword_query = f"""
                                        SELECT employers.employer_name, vacancies.vacancy_title,
                                        (vacancies.salary_from + vacancies.salary_to) / 2, vacancies.vacancy_url
                                        FROM vacancies
                                        JOIN employers ON vacancies.employer_id = employers.employer_id
                                        WHERE vacancy_title LIKE '%{keyword}%'
                                        ORDER BY employers.employer_name;
                                        """

        with self.connect_to_database() as connection:
            with connection.cursor() as cur:
                cur.execute(vacancies_with_keyword_query)
                res = cur.fetchall()
        connection.close()
        return res
