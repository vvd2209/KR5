# ������ �� �������� ������ � ��
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

# ������, ��� ����� �������� ������ ����������� �������� �� ���������� ����������.
# ��� ����� ������������ ��������� WHERE NOT EXISTS.
# ������ ���������� SELECT employer_name FROM employers WHERE employer_name = %s ���������,
# ���� �� ��� ������ � ����� �� ��������� employer_name � ������� employers.
# ���� ����� ������ ��� ����������, �� ������� �� �����������
insert_to_employers = """INSERT INTO employers (employer_name) 
                         SELECT %s
                         WHERE NOT EXISTS (
                         SELECT employer_name 
                         FROM employers
                         WHERE employer_name = %s)
                         """

# ������ ��� ������� ������ � ������� � ����������, ��� employer_id ���� �� ������� employers
insert_to_vacancies = """INSERT INTO vacancies (employer_id, vacancy_title, vacancy_url, vacancy_area,
                         salary_from, salary_to)
                         VALUES (%s, %s, %s, %s, %s, %s)
                         """

# ������ ������� ������ ������������� � ���������� ��������, ��������� � ������ �� ���, � ���������� �������
get_all_employers_query = """
                          SELECT employers.employer_name, COUNT(*) from employers
                          JOIN vacancies USING (employer_id)
                          GROUP BY employers.employer_name
                          ORDER BY employers.employer_name
                          """

# ������ ������� ���������� � �������������, ��������� ��������, ������� �������� � URL ��������,
# ��������������� �� �������� ������������
get_all_vacancies_query = """
                          SELECT employers.employer_name, vacancies.vacancy_title,
                          (vacancies.salary_from + vacancies.salary_to) / 2 AS average_salary, vacancies.vacancy_url
                          FROM vacancies
                          JOIN employers ON vacancies.employer_id = employers.employer_id
                          ORDER BY employers.employer_name;
                          """

# ������ ������� ������� �������� � ����� ������ ��� �������
get_avg_salary_query = "SELECT CAST(AVG((salary_from+salary_to)/2) AS INT) FROM vacancies"

# ������ ������� ���������� � �������������, ��������� ��������, ������� �������� � URL ��������,
# ������ ��� ��� ��������, � ������� ������� �������� ���� ������� �������� ���� ��������.
# ���������� ����������� �� �������� ������������.
get_high_salary_query = """
                        SELECT employers.employer_name, vacancies.vacancy_title, 
                        (vacancies.salary_from + vacancies.salary_to) / 2, vacancies.vacancy_url 
                        FROM vacancies 
                        JOIN employers ON vacancies.employer_id = employers.employer_id 
                        WHERE (vacancies.salary_from + vacancies.salary_to) / 2 >  
                        (SELECT CAST(AVG((vacancies.salary_from+vacancies.salary_to)/2) AS INT) FROM vacancies) 
                        ORDER BY employers.employer_name;
                        """
