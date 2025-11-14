To run MySQL Workbench and MySQL Server must be installed. A server must be created in the Workbench and linked to MySQL Server. This can be done by pressing the + sign next to MySQL Connections in the Workbench and entering the password created when setting up MySQL server. The Workbench should then automatically connect to the newly created server.

To run the schema script download 'Lobster Notes Import Data.sql' and run by pressing the lightning bolt in the Workbench toolbar.

To run the import script download 'Lobster Notes Import Data.sql' and any of the JSON files. Download the JSON files to a place where you can easily follow the path of. In the Query enter the following, with the file path in the load file.
insert into StageWebData(WebData)
values(LOAD_FILE(json path))
JSON contents will import when run.