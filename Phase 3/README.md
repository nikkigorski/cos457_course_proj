# cos457_course_proj
course project for usm class cos457 2025

Team name: Lobster Notes

Group members: Nikki Gorski(Nikki.Gorski@maine.edu), Gabrielle Akers(Gabrielle.Akers@maine.edu), Gage White(Gage.White@maine.edu) and Jove Emmons(Jove.Emmons@maine.edu)

Team leader: Nikki Gorski

Project topic: Creating a database when users can login, submit notes, see what resources their professors have verified, and rate other's notes for their classes

---

## How to run

### Setting up virtul environment
sudo apt install python3.12-venv

python3 -m venv lobstervenv

source lobstervenv/bin/activate

pip install -r requirements.txt

### Setting up MySQL

sudo apt install mysql-server

sudo service mysql start

sudo mysql_secure_installation

sudo mysql -u root -p

SET GLOBAL validate_password.policy = LOW;

SET GLOBAL validate_password.length = 4;

CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';

GRANT ALL PRIVILEGES ON lobsternotes.* TO 'admin'@'localhost';

FLUSH PRIVILEGES;

exit


### Running script

cd cos457_course_proj

./install

./run

---

## Github IDs

- Gabrielle (144271532)

- Gage (64271462)

- Nikki (126693450)

- Jove (144271740)

---

## Task breakdown

### Part 1 Roles

Gabrielle: ER diagram

Gage: Data dictionary

Nikki: Normal form discussion

Jove: Cardinality and participaion constraints

### Part 2 Roles

Gabrielle:	Database Structure & Constraints,	Schema Scripts, README

Gage:	Advanced Database Features,	Stored Procedures/Functions, Query Optimization

Nikki:	Data Acquisition & Cleaning,	Scraping Scripts, Sample Data/Cleaning Docs

Jove:	Integration & Presentation,	Video Demo, README - Editor

### Part 3 Roles

Gabrielle: Account creation, Video demo, README

Gage: Professor dashboard, Video demo, API doc

Nikki: Resource creation, Video demo, Setup guide

Jove: Topbar and Main page creation, Video demo, User manual
