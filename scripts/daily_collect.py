#!/usr/bin/env python3
"""
Meta Ads Intelligence -- Coleta Diaria Automatica
Roda todo dia pela manha via Agendador de Tarefas do Windows.
Coleta Google Sheets + processa dados.

Uso manual:
    python scripts/daily_collect.py
    python scripts/daily_collect.py --date-label 2026-03-18
"""

import argparse
import subprocess
import sys
import logging
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "daily_collect.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def run(cmd: list, label: str) -> bool:
    log.info(f"Iniciando: {label}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        log.info(f"OK: {label}")
        stdout = result.stdout or ""
        if stdout.strip():
            for line in stdout.strip().splitlines()[-10:]:
                log.info(f"  {line}")
    else:
        log.error(f"FALHOU: {label}")
        stderr = result.stderr or ""
        if stderr:
            log.error(stderr[-500:])
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Coleta diaria automatica")
    parser.add_argument("--date-label", default=str(date.today()))
    args = parser.parse_args()
    date_label = args.date_label

    log.info("=" * 60)
    log.info(f"COLETA DIARIA -- {date_label}")
    log.info("=" * 60)

    python = sys.executable
    scripts = PROJECT_ROOT / "scripts"

    steps = [
        (
            [python, str(scripts / "sheets_collector.py"), "--date-label", date_label],
            f"Google Sheets -> data/sheets/{date_label}_*.csv",
        ),
    ]

    ok = 0
    for cmd, label in steps:
        if run(cmd, label):
            ok += 1

    log.info("=" * 60)
    log.info(f"Concluido: {ok}/{len(steps)} etapas com sucesso")
    log.info("=" * 60)
    return 0 if ok == len(steps) else 1


if __name__ == "__main__":
    sys.exit(main())
