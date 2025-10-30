# Django-CRM
'''
├─ .github/
├─ .venv/
├─ accounts/
  ├─ migrations/
  │  ├─ 0001_initial.py
  │  ├─ 0002_initial.py
  │  ├─ 0003_alter_account_created_by.py
  ├─ __int__.py
  ├─ apps.py
  ├─ models.py
  ├─ serializer.py
  ├─ swagger_params1.py
  ├─ tasks.py
  ├─ tests_celery_tasks.py
  ├─ urls.py
  └─ views.py
├─ cases/
  ├─ __int__.py
  ├─ apps.py
  ├─ models.py
  ├─ serializer.py
  ├─ swagger_params1.py
  ├─ tasks.py
  ├─ tests_celery_tasks.py
  ├─ urls.py
  └─ views.py
├─ cms/
  ├─ migrations/
  ├─ templatestags
  ├─ __int__.py
  ├─ admin.py
  ├─ apps.py
  ├─ blocks.py
  ├─ models.p
  ├─ tests.py
  └─ views.py
├─ common/
  ├─ __pycache__/
  ├─ app_urls/
  ├─ context_processors/
  ├─ middelware/
  ├─ migrations/
  ├─ templates
  ├─ templatestags
  ├─ __int__.py
  ├─ access_decorator_mixins.py
  ├─ admin.py
  ├─ apps.py
  ├─ auth_backends.py
  ├─ auth_views.py
  ├─ base.py
  ├─ custom_auth.py
  ├─ custom_openapi.py
  ├─ external_auth.py
  ├─ manager.py
  ├─ mixins.py
  ├─ models.p
  ├─ permissions.py
  ├─ serializer.py
  ├─ status.py
  ├─ swagger_params1.py
  ├─ swagger_ui.html
  ├─ tasks.py
  ├─ tests_celery_tasks.py
  ├─ token_generator.py
  ├─ urls.py
  ├─ unils.py
  ├─ views.py
  └─ wagtail_hooks.py
├─ contacts/
  ├─ migrations/
  │  ├─ 0001_initial.py
  │  ├─ 0002_alter_contact_created_by.py
  │  ├─ 0003_alter_contact_secpmdary_number_and_more.py
  │  ├─ 0004_alter_contact_address.py
  │  └─ 0005_alter_contact_address.py
  ├─ __int__.py
  ├─ admin.py
  ├─ apps.py
  ├─ models.py
  ├─ serializer.py
  ├─ swagger_params1.py
  ├─ tasks.py
  ├─ tests_celery_tasks.py
  └─ urls.py
├─ crm/
  ├─ __int__.py
  ├─ celery.py
  ├─ server_settings.py
  ├─ settings.py
  ├─ urls.py
  └─ wsgi.py
├─ docs/ 
|   └─ Makefile
├─ emails/
  ├─ __init__.py
  ├─ admin.py
  ├─ apps.py
  ├─ forms.py
  ├─ models.py
  ├─ serialilzer.py
  ├─ tests.py
  ├─ urls.py
  └─ views.py
├─ events/
│  ├─ migrations/
│  ├─ templates/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ invoices/
│  ├─ migrations/
│  ├─ templates/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ api_urls.py
│  ├─ api_views.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ swagger_params.py
│  ├─ swagger_params1.py
│  ├─ tasks.py
│  ├─ tests_celery_tasks.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ leads/
│  ├─ migrations/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ swagger_params1.py
│  ├─ tasks.py
│  ├─ tests_celery_tasks.py
│  ├─ urls.py
│  └─ views.py
├─ opportunity/
│  ├─ migrations/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ swagger_params1.py
│  ├─ tasks.py
│  ├─ tests_celery_tasks.py
│  ├─ urls.py
│  └─ views.py
├─ planner/
│  ├─ migrations/
│  ├─ templates/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ scripts/
│  ├─ gunicorn.sh
│  └─ scripts
├─ static/assets
│  ├─ css/
│  ├─ img/
│  ├─ js/
│  └─ webfonts/
├─ tasks/
│  ├─ migrations/
│  ├─ templates/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ celery_tasks.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ swagger_params1.py
│  ├─ tests_celery_tasks.py
│  ├─ urls.py
│  ├─ utils.py
│  └─ views.py
├─ teams/
│  ├─ assiggned_to/
│  ├─ cms/
│  ├─ common/
│  ├─ registration/
│  ├─ base.html
│  ├─ cms_base.html
│  ├─ healthz.html
│  ├─ root_email_template_new.html
│  ├─ root_email_template.html
│  └─ root.html
├─ templates/
│  ├─ migrations/
│  ├─ templates/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ celery_tasks.py
│  ├─ models.py
│  ├─ serialilzer.py
│  ├─ swagger_params1.py
│  ├─ tests_celery_tasks.py
│  ├─ urls.py
│  ├─ utils.py
│  └─ views.py
├─ .coveragerc
├─ .deepsource.toml
├─ .env
├─ gitignore
├─ .pre-commit-config.yaml
├─ .runcode.yaml
├─ .travis.yml
├─ db.env
├─ docker-compose.yml
├─ Dockerfile11111
├─ dump.rdb
├─ ENV.md
├─ installation.md
├─ Jenkinsfile
├─ LICENSE
├─ manage.py
├─ MANIFEST.in
├─ pytest.in
├─ README.md
├─ requirements.txt
├─ schema.yaml
├─ schema.yml
├─ server.log
├─ setup.py
├─ Steps
└─ system_requirements.txt
'''

============

Django CRM is opensource CRM developed on django framework. It has all
the basic features of CRM to start with. We welcome code contributions
and feature requests via github.

This is divided into three parts
1. Backend API [Django CRM](https://github.com/MicroPyramid/Django-CRM)
2. Frontend UI [React CRM](https://github.com/MicroPyramid/react-crm "React CRM")
3. Mobile app [Flutter CRM]("https://github.com/MicroPyramid/flutter-crm")

## Runcode 

 Runcode is online developer workspace. It is cloud based simple, secure and ready to code workspaces, assuring high performance & fully configurable coding environment. With runcode you can run django-crm(API) with one-click.


- Open below link to create django-crm workspace on [RunCode](https://runcode.io/ "RunCode"). It will cretae django-crm API

    [![RunCode](https://runcode-app-public.s3.amazonaws.com/images/dark_btn.png)](https://runcode.io)

- After running API, Go to Frontend UI [React CRM](https://github.com/MicroPyramid/react-crm "React CRM") project to cretae new workpsace with runcode.

## Docs

Please [Click Here](http://django-crm.readthedocs.io "Click Here") for latest documentation.

## Project Modules
This project contains the following modules:
- Contacts
- Companies
- Leads
- Accounts
- Invoices (todo)
- Cases (todo)
- Opportunity (todo)

## Try for free [here](https://bottlecrm.io/)

## Installation Guide

We recommend ubuntu 20.04. These instructions are verified for ubuntu 20.04.

#### To install system requirments

```
sudo apt update && sudo apt upgrade -y

sudo apt install python-is-python3 xvfb libfontconfig wkhtmltopdf python3-dev python3-pip build-essential libssl-dev libffi-dev python3-venv redis-server redis-tools virtualenv -y
```

#### Install dependencies

##### Optional (based on personal choice)

```
sudo apt update && sudo apt upgrade -y && sudo apt install zsh python3-virtualenv

sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

pip install virtualenvwrapper

echo "source /home/ubuntu/.local/bin/virtualenvwrapper.sh" >> ~/.zshrc
```

If you want to install postgres, follow https://www.postgresql.org/download/
#### To modify postgresql root password

```
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'root';
```

#### Create and activate a virtual environment.
if you installed and configured virtualenv wrapper then use the following
``` 
mkvirtualenv <env_name>
workon <env_name>
```
or else
```
virtualenv venv
source venv/bin/activate
```
Install the project's dependency after activating env

```
pip install -r requirements.txt
```

### Env variables

* Then refer to `env.md` for environment variables and keep those in the `.env` file in the current folder as your project is in.


### Docker / docker-compose
in order to use docker, please run the next commands after cloning repo:
```
docker build -t djcrm:1 -f docker/Dockerfile .
docker-compose -f docker/docker-compose.yml up
```

**Note**: you must have docker/docker-compose installed on your host. 
### next steps


```
python manage.py migrate
python manage.py runserver
```
- Then open http://localhost:8000/swagger/ in your borwser to explore API.

- After running API, Go to Frontend UI [React CRM](https://github.com/MicroPyramid/react-crm "React CRM") project to configure Fronted UI to interact with API.


## Start celery worker in another terminal window

celery -A crm worker --loglevel=INFO

### Useful tools and packages

```
pipdeptree # to see pip dependancy tree
black # to format code to meet python coding standards
pip-check -H  # to see upgradable packages
isort # to sort imports in python
```

### Community

Get help or stay up to date.

-   [Issues](<https://github.com/MicroPyramid/Django-CRM/issues>)
-   Follow [@micropyramid](<https://twitter.com/micropyramid>) on Twitter
-   Ask questions on [Stack Overflow](<https://stackoverflow.com/questions/tagged/django-crm>)
-   Chat with community [Gitter](<https://gitter.im/MicroPyramid/Django-CRM>)
-   For customisations, email to <django-crm@micropyramid.com>

## Credits

### Contributors

This project exists thanks to all the people who contribute!

![image](https://opencollective.com/django-crm/contributors.svg?width=890&button=false)

### Feature requests and bug reports

We welcome your feedback and support, raise github issue if you want to
report a bug or request new feature. we are glad to help.

For commercial support [Contact us](https://micropyramid.com/contact-us/)

# Trigger deploy

