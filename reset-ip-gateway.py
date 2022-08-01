#!/usr/bin/env python

"""
Author: Ali Darraji
Purpose: Rboot multiple ST 2110 SDI-IP gateways with one button click.
"""

from tkinter import *
from tkinter import messagebox
import json
import requests
import logging
import os
from datetime import datetime
import csv

// 
if not os.path.exists("logs"):
    os.mkdir("logs")

logger = logging.getLogger()
handlr = logging.FileHandler("logs/log_{}.log".format(datetime.now().strftime("%Y_%m_%d_%H_%M")))
logger.addHandler(handlr)

root = Tk()

system_reset_body = {"reboot": "1", "config_reset": "0", "staging_mode": 0}
# system_resp_body = {"code": 200, "info": "system rebooting", "debug": null}


def get_ip_list():
    ip_list = []

    with open("flow_config.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        for line in csv_reader:
            if line[4] not in ip_list:
                ip_list.append(line[4])
    return ip_list


def req(host, resource, method="get", jsonbody=None, params=None):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.request(method=method, url=f"http://{host}/emsfp/node/v1/{resource}", headers=headers, data=json.dumps(jsonbody), params=params, timeout=3)
        if resp.status_code == 200:
            logger.error("%s  host %s   SUCCESS %s \n", str(datetime.now()), host, resp.status_code)
        else:
            messagebox.showerror("Error. ", resp.status_code)
            logger.error("%s Status code %s \n", str(datetime.now()), resp.status_code)
            resp.raise_for_status()

    # rare invalid HTTP response or regular unsuccesful (4xx/5xx) with Response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        messagebox.showerror(host, " HTTPError")
        logger.error("%s  host %s   HTTPError %s \n", str(datetime.now()), host, http_err)

    # network problem (e.g. DNS failure, refused connection, etc)
    except requests.exceptions.ConnectionError as conn_err:
        messagebox.showerror(host, " ConnectionError")
        logger.error("%s  host %s   ConnectionError %s \n", str(datetime.now()), host, conn_err)

    # request times out
    except requests.exceptions.Timeout as timeout_err:
        messagebox.showerror(host, " Timeout")
        logger.error("%s  host %s   Timeout %s \n", str(datetime.now()), host, timeout_err)

    # request exceeds the configured number of maximum redirections
    except requests.exceptions.TooManyRedirects as redirect_err:
        messagebox.showerror(host, " TooManyRedirects")
        logger.error("%s  host %s  TooManyRedirects %s \n", str(datetime.now()), host, redirect_err)

    # Other execptions
    except requests.exceptions.RequestException as e:
        messagebox.showerror(host, " RequestException")
        logger.error("%s host %s RequestException %s \n", str(datetime.now()), host, e)
        root.destroy()
        raise SystemExit(e)


def myClick():
    for host in get_ip_list():
        req(host, "self/system", method="PUT", jsonbody=system_reset_body)


root.geometry("400x200")
root.resizable(False, False)
root.title("RESET")

myButton = Button(root, text="RESET", padx=50, pady=20, command=myClick, fg="white", bg="#801515")
myButton.place(relx=0.5, rely=0.5, anchor=CENTER)


mainloop()
