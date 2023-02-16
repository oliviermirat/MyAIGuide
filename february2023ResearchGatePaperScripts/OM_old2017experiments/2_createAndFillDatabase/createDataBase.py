# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 16:59:28 2016

@author: Olivier
"""

import dataset
import sqlalchemy


def createTable(tab):

    tableName = tab.tableName
    columns = tab.m

    db = dataset.connect("sqlite:///olidata.db")

    db.query("DROP table IF EXISTS " + tableName)

    table = db.create_table(tableName)

    for row in columns:
        if row[2] == "int":
            table.create_column(row[0], sqlalchemy.Integer)
        elif row[2] == "varchar":
            table.create_column(row[0], sqlalchemy.VARCHAR(255))

    cols = ", ".join(columns[:, 0])
    db.query("DROP INDEX IF EXISTS unique_name")
    db.query("create unique index unique_name on " + tableName + "(" + cols + ")")

    print(db[tableName].columns)
