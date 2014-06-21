critikl
=======
Basic site monitoring in a single Python script,
with no dependencies.


### Features:

* Python 2 and Python 3 compatible
* No external deps
* Pushover notifications


### Usage:

* Edit the `config` in `critikl.py`

```python
config = {
    'interval': 60,  # How ofter to perform checks (in seconds)
    'pushover': {
        'app_token': 'your-pushover-app-token',
        'user_key': 'your-user-key',
    },
    'sites': {
        'example.com',  # Just the domain
        'https://example.com/api',  # OR a full url
    }
}
```


* Start the script

```bash
$ python critikl.py
```


* (Optional) Use a process manager (e.g. circus)

    A. Install circus

    ```bash
    $ sudo pip install circus
    ```

    B. Create the circus config file

    Edit `circus.ini` and modify the path
    where you put the `critikl.py` script

    ```bash
    $ nano circus.ini
    ```

    Create circus configuration file

    ```bash
    $ sudo cp circus.ini /etc/circus.ini
    ```

    Start circus (circus will start `critikl.py`)

    ```bash
    circusd /etc/circus.ini
    ```
    For more about circus, read [this](https://circus.readthedocs.org/en/0.11.1/)

    C. Start circus on system startup using upstart

    ```bash
    $ sudo cp circus.conf /etc/init/circus.conf
    $ sudo service circus start
    ```

That's it. You will now receive Pushover notifications
when one of your sites is down.
