from salt_spy import data, config

def run_import():
    import_file = config.config.LOGFILE
    db_file = config.config.DB

    db = data.Data(db_file)

    with open(import_file) as f:
        lines = f.readlines()
    for line in lines:
        db.insert_state_run(line)


if __name__ == '__main__':
    run_import()
