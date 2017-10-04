CREATE TABLE minion (
	minion_id integer PRIMARY KEY,
	name text NOT NULL UNIQUE
);

CREATE TABLE run (
	run_id integer PRIMARY KEY,
	minion_id integer,
	ret_time text,
	is_test integer,
	user text,
	UNIQUE (minion_id, ret_time),
	FOREIGN KEY (minion_id) REFERENCES minion (minion_id)
	ON DELETE CASCADE
);

CREATE TABLE state (
	state_id integer PRIMARY KEY,
	run_id integer,
	function text,
	__id__ text,
	__sls__ text,
	__run_num__ integer,
	comment text,
	changes text,
	name text,
	start_time text,
	duration real,
	result boolean,
	FOREIGN KEY (run_id) REFERENCES run (run_id)
	ON DELETE CASCADE
);
