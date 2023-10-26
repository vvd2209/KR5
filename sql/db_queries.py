# Запрос на создание таблиц в БД
create_tables = """
                CREATE TABLE IF NOT EXISTS employers (
                employer_id serial PRIMARY KEY,
                employer_name varchar NOT NULL
                );

                CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id serial PRIMARY KEY,
                employer_id int REFERENCES employers(employer_id) ON DELETE CASCADE,
                vacancy_title varchar(255) NOT NULL,
                vacancy_url varchar(150) NOT NULL,
                vacancy_area varchar(80),
                salary_from int,
                salary_to int
                );
                """

# Запрос, где перед вставкой данных выполняется проверка на отсутствие дубликатов.
# Для этого используется подзапрос WHERE NOT EXISTS.
# Внутри подзапроса SELECT employer_name FROM employers WHERE employer_name = %s проверяет,
# есть ли уже запись с таким же значением employer_name в таблице employers.
# Если такая запись уже существует, то вставка не выполняется
insert_to_employers = """INSERT INTO employers (employer_name) 
                         SELECT %s
                         WHERE NOT EXISTS (
                         SELECT employer_name 
                         FROM employers
                         WHERE employer_name = %s)
                         """

# Запрос для вставки данных в таблицу с вакансиями, где employer_id берём из таблицы employers
insert_to_vacancies = """INSERT INTO vacancies (employer_id, vacancy_title, vacancy_url, vacancy_area,
                         salary_from, salary_to)
                         VALUES (%s, %s, %s, %s, %s, %s)
                         """

# Запрос выводит список работодателей и количество вакансий, связанных с каждым из них, в алфавитном порядке
get_all_employers_query = """
                          SELECT employers.employer_name, COUNT(*) from employers
                          JOIN vacancies USING (employer_id)
                          GROUP BY employers.employer_name
                          ORDER BY employers.employer_name
                          """

# Запрос выводит информацию о работодателях, названиях вакансий, средней зарплате и URL вакансии,
# отсортированную по названию работодателя
get_all_vacancies_query = """
                          SELECT employers.employer_name, vacancies.vacancy_title,
                          (vacancies.salary_from + vacancies.salary_to) / 2 AS average_salary, vacancies.vacancy_url
                          FROM vacancies
                          JOIN employers ON vacancies.employer_id = employers.employer_id
                          ORDER BY employers.employer_name;
                          """

# Запрос выводит среднюю зарплату в целых числах без запятой
get_avg_salary_query = "SELECT CAST(AVG((salary_from+salary_to)/2) AS INT) FROM vacancies"

# Запрос выводит информацию о работодателях, названиях вакансий, средней зарплате и URL вакансии,
# только для тех вакансий, у которых средняя зарплата выше средней зарплаты всех вакансий.
# Результаты сортируются по названию работодателя.
get_high_salary_query = """
                        SELECT employers.employer_name, vacancies.vacancy_title, 
                        (vacancies.salary_from + vacancies.salary_to) / 2, vacancies.vacancy_url 
                        FROM vacancies 
                        JOIN employers ON vacancies.employer_id = employers.employer_id 
                        WHERE (vacancies.salary_from + vacancies.salary_to) / 2 >  
                        (SELECT CAST(AVG((vacancies.salary_from+vacancies.salary_to)/2) AS INT) FROM vacancies) 
                        ORDER BY employers.employer_name;
                        """
