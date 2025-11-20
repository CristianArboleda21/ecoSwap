# ECOSWAP

## Instalación

1. Clonar el repositorio:
   git clone https://github.com/CristianArboleda21/ecoSwap

2. Crear el entorno virtual

3. Instalar dependencias:
   pip install pipenv

4. Aplicar migraciones:
   python manage.py makemigrations (nombre_carpeta)
   python manage.py migrate

5. Ejecutar inserts:
   INSERT INTO publications_category (nombre) VALUES
   ('electronics'),
   ('home'),
   ('sports'),
   ('books'),
   ('clothing'),
   ('toys'),
   ('photography'),
   ('music'),
   ('accessories'),
   ('other');

   INSERT INTO publication_state (id) VALUES
   ('active'),
   ('inactive'),
   ('exchanged');

   INSERT INTO publications_condition (nombre) VALUES
   ('new'),
   ('excellent'),
   ('very-good'),
   ('good'),
   ('acceptable');

6. Ejecutar servidor:
   python manage.py runserver
