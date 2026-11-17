"""Deixa a raiz do projeto no sys.path, para os testes importarem `app` e `seed`."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
