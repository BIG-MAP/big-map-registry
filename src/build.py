#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from app_registry import build_from_config

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).parent.parent.resolve()
build_from_config(ROOT / "config.yaml")
