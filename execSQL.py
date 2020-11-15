def exec_sql_file(cursor, sql_file):
    print("\n[INFO] Executing SQL script file: '%s'" % (sql_file))
    statement = ""

    for line in open(sql_file):
        if line.strip().startswith('--'):  # ignore sql comment lines
            continue
        if not line.strip().endswith(';'):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
            cursor.execute(statement)

            statement = ""
            
def exec_proc_file(cursor, sql_file):
    print("\n[INFO] Executing SQL script file: '%s'" % (sql_file))
    statement = ""
    exec = False

    for line in open(sql_file):
        if line.strip().startswith('DELIMITER'):
            if exec:
                cursor.execute(statement)
                statement = ""
            exec = not exec
            continue
        if exec:
            if line.strip().startswith('--'):  # ignore sql comment lines
                continue
            if line.strip().endswith('//') or line.strip().endswith('$$'): 
                statement = statement + line[:-3]
            else:
                statement = statement + line