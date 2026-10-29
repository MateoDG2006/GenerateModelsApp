#!/usr/bin/env python3
"""Sincroniza tareas de Notion (base Tasksk, proyecto OrtesisLab) -> issues de GitHub.

Idempotente: solo procesa tareas cuya propiedad "GitHub Issue" esta vacia, y al
crear la issue escribe su URL de vuelta en la tarea. Correr de nuevo no duplica.

Variables de entorno:
  NOTION_TOKEN        (secreto) token de una integracion interna de Notion con acceso a la base Tasksk
  NOTION_DB_ID        id de la base Tasksk
  NOTION_PROJECT_ID   id de la pagina del proyecto (OrtesisLab) para filtrar
  GITHUB_TOKEN        token (lo provee GitHub Actions)
  GITHUB_REPOSITORY   "owner/repo" (lo provee GitHub Actions)
  DRY_RUN             "1" para no crear issues ni escribir (opcional)
"""
import json
import os
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DB_ID = os.environ["NOTION_DB_ID"]
PROJECT_ID = os.environ["NOTION_PROJECT_ID"]
GH_TOKEN = os.environ["GITHUB_TOKEN"]
GH_REPO = os.environ["GITHUB_REPOSITORY"]
DRY_RUN = os.environ.get("DRY_RUN") == "1"


def _req(url, method, headers, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit("HTTP %s en %s %s: %s" % (e.code, method, url, e.read().decode()))


def notion(method, path, payload=None):
    return _req("https://api.notion.com/v1" + path, method, {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }, payload)


def github(method, path, payload=None):
    return _req("https://api.github.com" + path, method, {
        "Authorization": "Bearer " + GH_TOKEN,
        "Accept": "application/vnd.github+json",
        "User-Agent": "notion-sync",
        "Content-Type": "application/json",
    }, payload)


def plain(rich):
    return "".join(t.get("plain_text", "") for t in rich)


def query_tasks():
    tasks, cursor = [], None
    flt = {"and": [
        {"property": "Proyectos", "relation": {"contains": PROJECT_ID}},
        {"property": "GitHub Issue", "url": {"is_empty": True}},
    ]}
    while True:
        payload = {"filter": flt, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        res = notion("POST", "/databases/%s/query" % NOTION_DB_ID, payload)
        tasks += res["results"]
        if res.get("has_more"):
            cursor = res["next_cursor"]
        else:
            break
    return tasks


def first_paragraph(page_id):
    try:
        res = notion("GET", "/blocks/%s/children?page_size=5" % page_id)
    except SystemExit:
        return ""
    for b in res.get("results", []):
        if b.get("type") == "paragraph":
            txt = plain(b["paragraph"]["rich_text"])
            if txt.strip():
                return txt
    return ""


def main():
    tasks = query_tasks()
    print("%d tarea(s) sin issue para OrtesisLab." % len(tasks))
    created = 0
    for t in tasks:
        props = t["properties"]
        title = plain(props["Nombre"]["title"]) or "(sin titulo)"
        prio = (props.get("Prioridad", {}).get("select") or {}).get("name")
        estado = (props.get("Estado", {}).get("status") or {}).get("name", "")
        desc = first_paragraph(t["id"])
        body = (
            "**Tarea de Notion:** %s\n\n"
            "**Prioridad:** %s  |  **Estado:** %s\n\n"
            "%s\n\n"
            "_Issue creada automaticamente desde la base Tasksk de Notion._"
            % (t["url"], prio or "-", estado, desc)
        )
        labels = [prio] if prio else []
        if DRY_RUN:
            print("[dry-run] crearia issue: %s" % title)
            continue
        issue = github("POST", "/repos/%s/issues" % GH_REPO,
                       {"title": title, "body": body, "labels": labels})
        url = issue["html_url"]
        notion("PATCH", "/pages/%s" % t["id"],
               {"properties": {"GitHub Issue": {"url": url}}})
        print("OK  %s -> %s" % (title, url))
        created += 1
    print("Listo. %d issue(s) creada(s)." % created)


if __name__ == "__main__":
    main()
