CREATE TABLE province (
    province_code CHAR(2) PRIMARY KEY,
    province_name TEXT NOT NULL UNIQUE
);

CREATE TABLE hunger_count (
    year SMALLINT NOT NULL,
    province_code CHAR(2) REFERENCES province(province_code),
    total_visits INTEGER NOT NULL CHECK (total_visits >= 0),
    child_visits INTEGER NOT NULL CHECK (child_visits BETWEEN 0 AND total_visits),
    reporting_food_banks INTEGER NOT NULL CHECK (reporting_food_banks > 0),
    comparable_to_2019 BOOLEAN NOT NULL,
    source_page SMALLINT NOT NULL,
    PRIMARY KEY (year, province_code)
);

CREATE TABLE food_insecurity (
    year SMALLINT NOT NULL,
    province_code CHAR(2) REFERENCES province(province_code),
    people_pct NUMERIC(4,1) NOT NULL CHECK (people_pct BETWEEN 0 AND 100),
    PRIMARY KEY (year, province_code)
);
