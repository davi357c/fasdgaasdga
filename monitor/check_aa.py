#!/usr/bin/env python3
"""Detecta modelos novos no Artificial Analysis.

Usa a API oficial se AA_API_KEY estiver definida; senão, raspa a página
de leaderboard. Guarda os modelos já vistos em monitor/seen_models.json
e imprime "NOVO: <modelo>" para cada modelo inédito.
"""
import json, os, re, sys, urllib.request
from pathlib import Path

STATE = Path(__file__).with_name("seen_models.json")
API = "https://artificialanalysis.ai/api/v2/data/llms/models"
PAGE = "https://artificialanalysis.ai/leaderboards/models"


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def get_models():
    key = os.environ.get("AA_API_KEY")
    if key:
        data = json.loads(fetch(API, {"x-api-key": key}))["data"]
        return {m["slug"]: m.get("name", m["slug"]) for m in data}
    html = fetch(PAGE)
    # Nomes e slugs aparecem no payload JSON embutido do Next.js
    slugs = re.findall(r'\\?"slug\\?":\\?"([a-z0-9][a-z0-9.\-]+)\\?"', html)
    return {s: s for s in slugs}


def main():
    models = get_models()
    if not models:
        sys.exit("Nenhum modelo encontrado (página mudou ou bloqueada).")
    seen = json.loads(STATE.read_text()) if STATE.exists() else None
    if seen is None:
        print(f"Primeira execução: {len(models)} modelos registrados como base.")
    else:
        new = [n for s, n in models.items() if s not in seen]
        for n in new:
            print(f"NOVO: {n}")
        if not new:
            print("Nenhum modelo novo.")
        models = {**seen, **models}
    STATE.write_text(json.dumps(models, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
