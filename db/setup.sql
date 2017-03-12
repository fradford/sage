drop table if exists waves;
create table waves (
  id integer primary key autoincrement,
  wave text not null
);
drop table if exists channels;
create table channels (
  id integer primary key autoincrement,
  channel text not null
);
