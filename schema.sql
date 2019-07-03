CREATE TABLE IF NOT EXISTS locations (
  name TEXT PRIMARY KEY,
  longitude NUMERIC NOT NULL,
  latitude NUMERIC NOT NULL,
  geoname_result JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS profiles (
  profile_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  image_url TEXT NOT NULL,
  directory_url TEXT NOT NULL,
  location TEXT
    REFERENCES locations(name)
);
