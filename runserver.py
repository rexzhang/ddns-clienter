#!/usr/bin/env python
# coding=utf-8


import uvicorn


def main():
    kwargs = {
        "host": "0.0.0.0",
        "port": 8000,
        "app": "ddns_clienter.asgi:application",
        # TODO: ASGI 'lifespan' protocol appears unsupported. Django 3.1.x
        "lifespan": "off",
        "access_log": False,
    }

    uvicorn.run(**kwargs)


if __name__ == "__main__":
    main()
