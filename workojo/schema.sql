DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS workout;
DROP TABLE IF EXISTS diet_goals;
DROP TABLE IF EXISTS exercise;
DROP TABLE IF EXISTS macros;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE workout (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tag TEXT NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES user (id)  
);

CREATE TABLE diet_goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  daily_protein INTEGER NOT NULL,
  daily_carbs INTEGER NOT NULL,
  daily_fats INTEGER NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES user (id)
);

CREATE TABLE macros (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workout_id INTEGER NOT NULL,
  protein INTEGER NOT NULL,
  carbs INTEGER NOT NULL,
  fats INTEGER NOT NULL,
  FOREIGN KEY (workout_id) REFERENCES workout (id)
);

CREATE TABLE exercise (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workout_id INTEGER NOT NULL,
  exercise_name TEXT NOT NULL,
  set_number INTEGER NOT NULL,
  repetitions INTEGER NOT NULL,
  unit TEXT NOT NULL,
  FOREIGN KEY (workout_id) REFERENCES workout (id)
);