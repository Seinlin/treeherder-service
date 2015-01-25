Installation
================

Cloning the Repo
----------------

* Clone the `treeherder-service repo`_ from Github.

Setting up Vagrant
------------------

* Install Virtualbox_ and Vagrant_ if not present.

* Either follow the :doc:`ui_integration` steps, or comment out this line in the Vagrantfile:

  .. code-block:: ruby

     config.vm.synced_folder "../treeherder-ui", "/home/vagrant/treeherder-ui", type: "nfs"

* Open a shell, cd into the root of the project you just cloned and type

  .. code-block:: bash

     >vagrant up

* Go grab a tea or coffee, it will take a few minutes to setup the environment.

* Once the virtual machine is set up, you can log into it with

  .. code-block:: bash

     >vagrant ssh

* A python virtual environment will be activated on login, all that is left to do is cd into the project directory:

  .. code-block:: bash

     (venv)vagrant@precise32:~$ cd treeherder-service

* Build the log parser Cython files, since they are required for both running the tests and a local Treeherder instance

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ python setup.py build_ext --inplace

  NB: If you change something in the treeherder/log_parser folder, remember to repeat this step, otherwise the changes will not take effect.

Running the tests
------------------------

* The tests can be run without following the local instance steps below.

* You can run the py.test suite with

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ ./runtests.sh

Setting up a local Treeherder instance
---------------------

* Initialize the master database

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ python manage.py init_master_db

* Populate the database with repository data sources

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ python manage.py init_datasources

* Export oauth credentials for all data source projects

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ python manage.py export_project_credentials

* And an entry to your host machine /etc/hosts so that you can point your browser to local.treeherder.mozilla.org to reach it

  .. code-block:: bash

     192.168.33.10    local.treeherder.mozilla.org

Viewing the local server
------------------------

* Start a gunicorn instance listening on port 8000

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ ./bin/run_gunicorn

  all the request sent to local.treeherder.mozilla.org will be proxied to it by varnish/apache.


* Or for development you can use the django runserver instead of gunicorn:

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ python manage.py runserver

  this is more convenient because it automatically refreshes every time there's a change in the code.

* Visit http://local.treeherder.mozilla.org in your browser. Note: There will be no data to display until the ingestion tasks are run.

Running the ingestion tasks
---------------------------

* Ensure the django runserver or gunicorn instance is running first.

* In another Vagrant SSH session, start up a celery worker to process async tasks:

  .. code-block:: bash

     (venv)vagrant@precise32:~/treeherder-service$ celery -A treeherder worker -B

  The "-B" option tells the celery worker to startup a beat service, so that periodic tasks can be executed.
  You only need one worker with the beat service enabled. Multiple beat services will result in periodic tasks being executed multiple times



.. _treeherder-service repo: https://github.com/mozilla/treeherder-service
.. _Vagrant: https://www.vagrantup.com
.. _Virtualbox: https://www.virtualbox.org
