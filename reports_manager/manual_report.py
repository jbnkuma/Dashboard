#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8

import sys

from dashboard import db, servers, services_status, changes, incidents, downtime_logbook
from novell_libraries.dashboard_utils import CreateReport

generate = CreateReport()
if len(sys.argv) == 3:
    year = sys.argv[1]
    month = sys.argv[2]
    print generate.create_excel2(db, servers, services_status, changes, incidents, year, month, downtime_logbook)
