sudo -i -u postgres
psql

# drop database yahoo;

create database yahoo owner terrence
\c yahoo

create table users (user_pk serial NOT NULL, user_id char(20) default '', access_token varchar default '',token_type char(15) default '',expires_in char(20) default '',xoauth_yahoo_guid varchar default '',refresh_token varchar default '',league_id varchar default '');

alter table users owner to terrence;
