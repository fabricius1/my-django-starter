import configparser
import sys
import os
import re
import io


# about config_info:
# - make changes inside this variable;
# - only change the information after the equal signs;
# - don't write/use quotes (it's already a multiline string);
# - separate the apps names with commas and no spaces.
config_info = f"""
[DJANGO]

PYTHON_ALIAS=python
VENV_NAME=.myenv
PROJECT_FOLDER=films_project
PROJECT_NAME=project_main
APPS=films,budget,public,authentication
LANGUAGE=pt-br
TIMEZONE=America/Sao_Paulo
"""

# set the config object
buffer = io.StringIO(config_info)
config = configparser.ConfigParser()
config.read_file(buffer)

# save individual variables from the config_info variable above
python_alias = config['DJANGO']['PYTHON_ALIAS']
venv_name = config['DJANGO']['VENV_NAME']
project_folder = config['DJANGO']['PROJECT_FOLDER']
project_name = config['DJANGO']['PROJECT_NAME']
django_apps = config['DJANGO']['APPS']
language = config['DJANGO']['LANGUAGE']
timezone = config['DJANGO']['TIMEZONE'] 


# set apps_list as a Python list with all apps names
if ',' in django_apps:
    apps_list = [x.strip() for x in django_apps.split(',') if x]
else:
    apps_list = [django_apps]

    
# define 3 functions to create the Django app(s) later:
def modify_views_py(app_name):
    """
    Rewrite the respective 'views.py' file from the current django app
    with a basic function view called '{app_name}_starter', which returns
    a <h1> HTML element as its response.
    
    Parameter:
    - app_name(str): the django app name.
    
    Return:
    - None
    """
    with open(os.path.join(app_name, 'views.py'), 'w') as file:
        views_file_content=(
            'from django.http import HttpResponse\n\n'
            f'def {app_name}_starter(request):\n'
            f'    return HttpResponse("<h1>{app_name.upper()} PAGE</h1>")\n'
        )
        file.write(views_file_content)


def create_urls_py(app_name):
    """
    Create a 'urls.py' file inside the folder from the current django app
    with a route named '{app_name}_all'. This '{app_name}/urls.py' file will be included
    in the entrypoint '{project_name}/urls.py' later.
    
    Parameter:
    - app_name(str): the django app name.
    
    Return:
    - None
    """

    urls_file_content = ('from django.urls import path\n'
                         'from . import views\n\n'
                         f"app_name = '{app_name}'\n\n"
                         'urlpatterns = [\n'
                         f"    path('', views.{app_name}_starter,"
                         f"name='{app_name}_all')\n"
                         ']')
        
    with open(os.path.join(app_name, 'urls.py'), 'w') as file:
        file.write(urls_file_content)


def create_new_django_app(app_name, python_alias='python', index=''):
    """
    Start the Django app in the app_name parameter, create its 
    template folders, make modifications to its 'views.py' file and
    create a 'urls.py' for the app.
    
    Parameters:
    - app_name(str): the django app name.
    - python_alias (str): it is the alias your terminal uses to call 
    the Python executable. For me, it is 'python' in my Windows and
    'python3' in my Ubuntu WSL terminal. This info goes on this function
    first executed terminal command.
    - index (int, later used as str): you won't need to change this
    attribute, it will use the index from the enumerate() function
    called in the for loop that creates the django apps later in this
    script
    
    Return:
    - None
    """
    
    # start app
    os.system(f'{python_alias} manage.py startapp {app_name}')
    
    # create templates folder structure
    os.makedirs(os.path.join(app_name, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(app_name, 'templates', app_name), exist_ok = True)
    
    # modify {app_name}/views.py
    modify_views_py(app_name)   
    
    # create {app_name}/urls.py 
    create_urls_py(app_name)
            
    # print console information
    if index:
        print(f"Created Django app ({index}): {app_name}")
    else:
        print(f"Created Django app: {app_name}")


# MAIN SCRIPT STARTS HERE

# create the main project folder and move inside it:
try:
    os.makedirs(project_folder)
    os.chdir(project_folder)
    print(f'\nCreated project folder: {project_folder}')
except:
    # finish the script if project_folder already exists.
    print(f'\nThere is already a folder called {project_folder}. Script finished.\n')
    sys.exit(1)

# create a virtual environment with venv
print('Creating virtual environment...')
os.system(f'{python_alias} -m venv {venv_name}')
print(f'Created virtual environment: {venv_name}')

# create the Django project
os.system(f'django-admin startproject {project_name} .')
print(f'Created Django project: {project_name}')

# create the Django app(s)
apps_count = 0
for index, app in enumerate(apps_list):
    create_new_django_app(app, python_alias, index=index+1)
    apps_count += 1

# make changes to the main {project_name}/urls.py file
urls_py_path = os.path.join(project_name, 'urls.py')

with open(urls_py_path) as file:
    content = file.read()
    
    # remove initial multiline string with observations about urls.py
    pattern = re.compile(r'\"\"\".*?\"\"\"\n{1,5}', re.DOTALL)
    content = pattern.sub('', content)
    
    # import the include() function and add a temporary view function
    pattern = re.compile('import path\n', re.DOTALL)
    new = ('import path, include\n'
           'from django.http import HttpResponse'
           ' # remove this import later\n\n'
           '# remove this function later:\n'
           'def starter_home(request):\n'
           '    return HttpResponse("<h1>HOME PAGE</h1>")\n\n')
    content = pattern.sub(new, content)
    
    # insert path to home page with the temporary function view we created
    pattern = re.compile(r'\[\n    ', re.DOTALL)
    new = (r"[\n    path('', starter_home, name='home'),\n    ")
    content = pattern.sub(new, content)
    
    # insert the app(s) route(s)
    new = ''
    for app in apps_list:
        new += f"    path('{app}/', include('{app}.urls')),\n"
    
    content = content.replace(']', new + ']')
    
# save the new {project_name}/urls.py file
with open(urls_py_path, 'w') as file:
    file.write(content)

print(f"Updated {project_name}/urls.py file")


# create extra folders
extra_folders = ['templates',
                 os.path.join('templates', 'static'),
                 'media',
                 'scripts']

for folder in extra_folders:
    os.makedirs(folder, exist_ok=True)
    
print('Created extra folders')

# make changes to the settings.py file
setting_py_path = os.path.join(project_name, 'settings.py')

with open(setting_py_path) as file:
    content = file.read()
    
    # remove initial multiline string about settings.py
    pattern = re.compile(r'\"\"\".*?\"\"\"\n{1,5}', re.DOTALL)
    content = pattern.sub('', content)

    # insert an import to the 'os' module
    pattern = re.compile('from pathlib import Path\n', re.DOTALL)
    content = pattern.sub('from pathlib import Path\nimport os\n', content)

    # insert django_extensions in INSTALLED_APPS
    pattern = re.compile("'django.contrib.staticfiles',\n", re.DOTALL)
    new_string = ("'django.contrib.staticfiles',\n\n"
                  "    # aditional packages:\n"
                  "    'django_extensions',\n\n"
                  "    # personal apps:\n")
    
    # insert the app(s) name(s) in INSTALLED_APPS
    for app in apps_list:
        new_string += f"    '{app}',\n"
                  
    content = pattern.sub(new_string, content)
    
    # insert templates DIR info
    pattern = re.compile(r"'DIRS': \[\],\n", re.DOTALL)
    new = r"'DIRS': [os.path.join(BASE_DIR, 'templates')],\n"
    content = pattern.sub(new, content)
    
    # change language, if necessary
    if language:
        content = content.replace('en-us', language)
        
    # change timezone, if necessary
    if timezone:
        content = content.replace('UTC', timezone)
        
    # change static info and add media info
    new = ("STATIC_URL = '/static/'\n"
           "STATICFILES_DIRS = (os.path.join(BASE_DIR, 'templates', 'static'),)\n"
           "STATIC_ROOT = os.path.join('static')\n\n"
           "MEDIA_ROOT = os.path.join(BASE_DIR, 'media')\n"
           "MEDIA_URL = '/media/'\n"
        )
    pattern = re.compile("STATIC_URL = 'static/'\n", re.DOTALL)
    content = pattern.sub(new, content)
    
# save the new settings.py file
with open(setting_py_path, 'w') as file:
    file.write(content)

print(f'Updated {project_name}/settings.py file')
print('\nEnd of the script')
print('Thanks for using my-django-starter!\n')
