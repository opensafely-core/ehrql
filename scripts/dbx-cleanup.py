# Databricks notebook source
dbutils.fs.ls("/user/hive/warehouse")

for path in dbutils.fs.ls("/user/hive/warehouse"):
    print(f"Deleteing {path.path}")
    dbutils.fs.rm(path.path, recurse=True)
