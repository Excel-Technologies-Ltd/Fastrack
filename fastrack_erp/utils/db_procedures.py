"""
Helpers for the hand-written MySQL stored procedures kept in this app's
Database/ folder (apps/fastrack_erp/Database/*.sql) -- a sibling of the
importable app package, not part of it, since these are plain .sql source
files rather than Python.

Two responsibilities:
  - call_procedure(): safely CALL one of them from report code.
  - sync_stored_procedures(): (re)create all of them in the database,
    registered as an after_migrate hook so the database never drifts from
    what's committed in Database/ -- previously these had to be applied by
    hand after every change.
"""

import os
import re

import frappe
import pymysql


def call_procedure(name, params):
	"""Call a MySQL stored procedure on a separate, throwaway connection.

	A stored procedure's own SELECTs return normally, but a MySQL CALL
	always leaves an extra "procedure status" result set behind on the
	connection afterwards. frappe.db.sql() only reads the first result set
	and never drains that trailing one, which then makes every later query
	on that same shared connection fail with "Commands out of sync". Using
	a separate connection (built from frappe's own settings) means the
	stored procedure call can't corrupt the connection the rest of the
	request relies on.
	"""
	placeholders = ", ".join(["%s"] * len(params))

	connection = frappe.db.create_connection()
	try:
		with connection.cursor(pymysql.cursors.DictCursor) as cursor:
			cursor.execute(f"CALL {name}({placeholders})", params)
			data = cursor.fetchall()
			while cursor.nextset():
				pass
		return data
	finally:
		connection.close()


def get_database_folder():
	"""apps/fastrack_erp/Database -- sibling of the importable app package
	(apps/fastrack_erp/fastrack_erp), so frappe.get_app_path alone doesn't
	reach it."""
	app_package_path = frappe.get_app_path("fastrack_erp")
	return os.path.abspath(os.path.join(app_package_path, "..", "Database"))


def split_sql_statements(sql_text):
	"""Split a .sql file that uses the mysql CLI's `DELIMITER` directive
	(needed so a CREATE PROCEDURE body full of semicolons can be written as
	one statement) into individual statements a DB-API cursor can run one
	at a time -- cursor.execute() has no idea what DELIMITER means, it's a
	mysql-client-only convention, not real SQL."""
	statements = []
	delimiter = ";"
	buffer = []

	def flush():
		text = "\n".join(buffer).strip()
		if not text:
			return
		if text.endswith(delimiter):
			text = text[: -len(delimiter)]
		text = text.strip()
		if text:
			statements.append(text)

	for line in sql_text.splitlines():
		match = re.match(r"^\s*DELIMITER\s+(\S+)\s*$", line, re.IGNORECASE)
		if match:
			flush()
			buffer = []
			delimiter = match.group(1)
			continue

		buffer.append(line)
		if "\n".join(buffer).rstrip().endswith(delimiter):
			flush()
			buffer = []

	flush()
	return statements


def sync_stored_procedures():
	"""Recreate every stored procedure defined in Database/*.sql. Runs after
	every `bench migrate` (see hooks.py's after_migrate) so the database's
	procedures never drift from source control."""
	folder = get_database_folder()
	if not os.path.isdir(folder):
		return

	sql_files = sorted(f for f in os.listdir(folder) if f.endswith(".sql"))
	if not sql_files:
		return

	synced, failed = [], []
	connection = frappe.db.create_connection()
	try:
		with connection.cursor() as cursor:
			for filename in sql_files:
				path = os.path.join(folder, filename)
				with open(path) as f:
					sql_text = f.read()

				try:
					for statement in split_sql_statements(sql_text):
						cursor.execute(statement)
					synced.append(filename)
				except Exception:
					failed.append(filename)
					frappe.log_error(
						title=f"Failed to sync stored procedure: {filename}",
						message=frappe.get_traceback(),
					)
		connection.commit()
	finally:
		connection.close()

	if synced:
		print(f"Synced {len(synced)} stored procedure(s) from Database/: {', '.join(synced)}")
	if failed:
		print(f"Failed to sync {len(failed)} stored procedure(s): {', '.join(failed)} (see Error Log)")
