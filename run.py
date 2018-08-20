#!/usr/bin/env python
# run.py

if __name__ == "__main__":
    from numpy.random import randint
    import threading
    import webbrowser

    from vindta_reCAlk import app

    port = 5000

    url = "http://localhost:{:d}/".format(port)
    threading.Timer(2, lambda: webbrowser.open(url)).start()

    app.run(port=port, debug=True)
