import requests
import json
from datetime import datetime, timedelta, timezone
import csv
import os
import re
import time
import sys

def format_findings_for_telegram(findings):
    def escape_html(text):
        return re.sub(r"[<>&]", lambda x: {"<": "&lt;", ">": "&gt;", "&": "&amp;"}[x.group()], text)
    message=False
    for finding in findings:
        severity=finding["severity"]
        template=finding["template"]

        if severity!="high" and severity!="critical":
            continue
        if severity=="high":
            message = f"🟠<b>{template}</b>🟠\n"
        if severity=="critical":
            message = f"⭐<b>{template}</b>⭐\n"
        message+=f"\n"

    return message

def parse_nuclei(file):
    findings = []
    pattern = re.compile(
        r"\[(?P<template>[^\]]+)\]\s+"
        r"\[(?P<protocol>[^\]]+)\]\s+"
        r"\[(?P<severity>[^\]]+)\]\s+"
        r"(?P<rest>.+)"
    )


    with open(file, "r") as f:
        for line in f:
            line = line.strip()  # removes \n
            match = pattern.match(line)
            if not match:
                continue  # or log invalid lines
            findings.append(match.groupdict())
    message=format_findings_for_telegram(findings)
    send_telegram_message(message,file)


def send_telegram_message(message,file):

    token = os.getenv('TELEGRAM_BOT')
    chat_id = os.getenv('TELEGRAM_GROUP')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    if message is not False:
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    if file and os.path.exists(file) and os.path.getsize(file) > 0:
        document_url = f"https://api.telegram.org/bot{token}/sendDocument"
        try:
            with open(file, "rb") as f:
                r = requests.post(
                    document_url,
                    data={"chat_id": chat_id},
                    files={"document": f},
                    timeout=60,
                )
                r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"File error: {e}")
            return None





def main():
    if len(sys.argv) != 2:
        print("Usage: python send_nuclei_tg.py <file_path>")
        sys.exit(1)
    parse_nuclei(sys.argv[1])


if __name__ == "__main__":
    main()