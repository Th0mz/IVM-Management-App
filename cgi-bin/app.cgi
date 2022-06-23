#!/usr/bin/python3
from wsgiref.handlers import CGIHandler
from flask import Flask
from flask import render_template, request

# database adapter
import psycopg2
import psycopg2.extras

# SGBD config
DB_HOST = "db.tecnico.ulisboa.pt"
with open("./cgi-bin/auth.txt") as auth:
	DB_USER = auth.readline().replace("\n", "")
	DB_PASSWORD = auth.readline().replace("\n", "")
DB_DATABASE = DB_USER
DB_CONNECTION_STRING = f"host={DB_HOST} dbname={DB_DATABASE} user={DB_USER} password={DB_PASSWORD}"

# environment variables
HOME_PATH = "cgi-bin/"
APP_PATH = HOME_PATH + "app.cgi/"

# category
CATEGORY_PATH = APP_PATH + "category/"
SUPER_CATEGORY_PATH = CATEGORY_PATH + "super/"
SUPER_VIEW_PATH = SUPER_CATEGORY_PATH + "view/?category_name="

SIMPLE_CATEGORY_PATH = CATEGORY_PATH + "simple/"

# retailer
RETAILER_PATH = APP_PATH + "retailer/"

# ivm
IVM_PATH = APP_PATH + "ivm/"



# table max size
TABLE_SIZE = 10

# tables
CATEGORY_TABLE = "category"
SUPER_CATEGORY_TABLE = "super_category"
SIMPLE_CATEGORY_TABLE = "simple_category"
HAS_OTHER_TABLE = "has_other"
IVM_TABLE = "ivm"
REPLENISHMENT_TABLE = "replenishment_event"

# columns
CATEGORY_KEY = "category_name"
SUPER_CATEGORY = "super_category"
SUBCATEGORY = "category"
SERIAL_NUMBER = "serial_num"
SUPPLIER = "supplier"
UNITS = "units"
EAN = "ean"

app = Flask(__name__)

def dbConnect():
	dbConn = psycopg2.connect(DB_CONNECTION_STRING)
	cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	return (dbConn, cursor)

###############################################################
#                                                             #
#                         M A I N                             #   
#                                                             #
###############################################################

@app.route("/")
def HOME_PATH():
        return render_template("main.html", category=CATEGORY_PATH, retailer=RETAILER_PATH, ivm=IVM_PATH)

###############################################################
#                                                             #
#                     C A T E G O R Y                         #   
#                                                             #
###############################################################

@app.route("/category/")
def category():
        return render_template("category.html", app=APP_PATH, super_category=SUPER_CATEGORY_PATH, simple_category=SIMPLE_CATEGORY_PATH)

# ------------------------------------------------------------ #
#                       S I M P L E                            #
# ------------------------------------------------------------ #
@app.route("/category/simple/")
def simpleCategory():
        cursor = None
        dbConn = None

        try:
                # get current page
                page = request.args.get("page")
                if (page == None):
                        page = 0

                page = int(page)
                page_offset = page * TABLE_SIZE
                query = f"SELECT * FROM {SIMPLE_CATEGORY_TABLE} OFFSET {page_offset} FETCH FIRST {TABLE_SIZE} ROWS ONLY"
                dbConn, cursor = dbConnect()
                cursor.execute(query)

                return render_template("simpleCategories.html", cursor=cursor, page=page, simple=SIMPLE_CATEGORY_PATH, category=CATEGORY_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SIMPLE_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/category/simple/remove/")
def removeSimpleCategory():
        cursor = None
        dbConn = None

        try:
                # connect to the database
                dbConn, cursor = dbConnect()
                category_name = request.args.get("category_name")

                # delete all relations with its subcategories and its supercategories
                query = f"DELETE FROM {HAS_OTHER_TABLE} WHERE {SUBCATEGORY} = %s;"
                cursor.execute(query, (category_name,))

                # delete category_name from simple category table
                query = f"DELETE FROM {SIMPLE_CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                # delete category_name from super category table
                query = f"DELETE FROM {CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                # commit changes
                dbConn.commit()
                title = "Remove"
                text = f"Successfully removed the category \'{ category_name }\'"

                return render_template("prompt.html", title=title, text=text, return_to=SIMPLE_CATEGORY_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SIMPLE_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()




# ------------------------------------------------------------ #
#                        S U P E R                             #
# ------------------------------------------------------------ #
@app.route("/category/super/")
def superCategory():
	cursor = None
	dbConn = None

	try:
                # get current page
                page = request.args.get("page")
                if (page == None):
                       page = 0

                page = int(page)
                page_offset = page * TABLE_SIZE
                query = f"SELECT * FROM {SUPER_CATEGORY_TABLE} OFFSET {page_offset} FETCH FIRST {TABLE_SIZE} ROWS ONLY"
                dbConn, cursor = dbConnect()
                cursor.execute(query)

                return render_template("superCategories.html", cursor=cursor, page=page, super=SUPER_CATEGORY_PATH, category=CATEGORY_PATH)
	except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
	finally:
		cursor.close()
		dbConn.close()


@app.route("/category/super/add/", methods=["POST"])
def addSuperCategory():
        cursor = None
        dbConn = None

        try:
		# connect to the database
                dbConn, cursor = dbConnect()
                category_name = request.form["category_name"]
                
		# insert value into category table
                query = f"INSERT INTO {CATEGORY_TABLE} VALUES (%s);"
                cursor.execute(query, (category_name,))

                # insert value into super category table
                query = f"INSERT INTO {SUPER_CATEGORY_TABLE} VALUES (%s);"
                cursor.execute(query, (category_name,))

		# commit changes
                dbConn.commit()
                title = "Add"
                text = f"Successfully added the category \'{category_name}\'"

                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/category/super/add/has/", methods=["POST"])
def addToSuperCategory():
        cursor = None
        dbConn = None

        try:
		# connect to the database
                dbConn, cursor = dbConnect()
                super_category_name = request.form["super_category_name"] 
                category_name = request.form["category_name"]

                # TODO : and check this recusivly
                if (super_category_name == category_name):
                        title = "Error"
                        text = f"A category cannot be subcategory of itself"
                        return render_template("prompt.html", title=title, text=text, return_to=(SUPER_VIEW_PATH + super_category_name)) 

                # TODO : check if the relation already exists 

                # check if super_category exists
                query = f"SELECT * FROM {SUPER_CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (super_category_name,))

                if (cursor.rowcount == 0):
                        title = "Error"
                        text = f"The super category \'{ super_category_name }\', does not exist"
                        return render_template("prompt.html", title=title, text=text, return_to=(SUPER_VIEW_PATH + super_category_name))
                
                # check if subcategory exists
                query = f"SELECT * FROM {CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                if (cursor.rowcount == 0):
                        # if it doesnt exist create it as a simple_category
                        query = f"INSERT INTO {CATEGORY_TABLE} VALUES (%s);"
                        cursor.execute(query, (category_name,))

                        query = f"INSERT INTO {SIMPLE_CATEGORY_TABLE} VALUES (%s);"
                        cursor.execute(query, (category_name,))

                # add the relation between categories
                query = f"INSERT INTO {HAS_OTHER_TABLE} VALUES (%s, %s);"
                cursor.execute(query, (super_category_name, category_name))

                # commit changes
                dbConn.commit()

                title = "Success"
                text = f"Successfully added the category \'{category_name}\' to \'{super_category_name}\'"

                return render_template("prompt.html", title=title, text=text, return_to=(SUPER_VIEW_PATH + super_category_name))
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/category/super/remove/")
def removeSuperCategory():
        cursor = None
        dbConn = None

        try:
                # connect to the database
                dbConn, cursor = dbConnect()
                category_name = request.args.get("category_name")

                # delete all relations with its subcategories and its supercategories
                query = f"DELETE FROM {HAS_OTHER_TABLE} WHERE {SUPER_CATEGORY} = %s OR {SUBCATEGORY} = %s;"
                cursor.execute(query, (category_name, category_name))

                # delete category_name from super category table
                query = f"DELETE FROM {SUPER_CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                # delete category_name from super category table
                query = f"DELETE FROM {CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                # commit changes
                dbConn.commit()
                title = "Remove"
                text = f"Successfully removed the category \'{ category_name }\'"

                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/category/super/remove/has/")
def removeFromSuperCategory():
        cursor = None
        dbConn = None

        try:
		# connect to the database
                dbConn, cursor = dbConnect()
                super_category_name = request.args.get("super_category_name") 
                category_name = request.args.get("category_name") 

                # add the relation between categories
                query = f"DELETE FROM {HAS_OTHER_TABLE} WHERE {SUPER_CATEGORY} = %s AND {SUBCATEGORY} = %s;"
                cursor.execute(query, (super_category_name, category_name))

                # commit changes
                dbConn.commit()

                title = "Success"
                text = f"Successfully removed \'{category_name}\' from \'{super_category_name}\'"

                return render_template("prompt.html", title=title, text=text, return_to=(SUPER_VIEW_PATH + super_category_name))
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/category/super/view/")
def viewSuperCategory():
        cursor = None
        dbConn = None

        try:
                # connect to the database
                dbConn, cursor = dbConnect()
                category_name = request.args.get("category_name")

                # check if the category exists
                query = f"SELECT * FROM {SUPER_CATEGORY_TABLE} WHERE {CATEGORY_KEY} = %s"
                cursor.execute(query, (category_name,))

                if (cursor.rowcount == 0):
                        title = "Error"
                        text = f"The super category \'{ category_name }\', does not exist"
                        return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)

                # get all of its subcategories recursivly
                subcategories = recursiveSubcategoryGet(cursor, category_name, 0)

                return render_template("superCategoryView.html", subcategories=subcategories, category_name=category_name, super=SUPER_CATEGORY_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=SUPER_CATEGORY_PATH)
        finally:
                cursor.close()
                dbConn.close()


def recursiveSubcategoryGet (cursor, category_name, lvl):
        query = f"SELECT * FROM {HAS_OTHER_TABLE} WHERE {SUPER_CATEGORY} = %s"
        cursor.execute(query, (category_name,))

        if (cursor.rowcount == 0):
                return []

        subcategories = []
        records = copyRecords(cursor)
        for record in records:
                subcategory_name = record[1]
                subcategories.append([lvl, subcategory_name, recursiveSubcategoryGet(cursor, subcategory_name, lvl + 1)])

        return subcategories

def copyRecords (cursor):
        records = []
        for record in cursor:
                records.append(record)
        
        return records




###############################################################
#                                                             #
#                      R E T A I l E R                        #   
#                                                             #
###############################################################

@app.route("/retailer/")
def retailer():
        return render_template("retailerMain.html", app=APP_PATH)



###############################################################
#                                                             #
#                          I V M                              #   
#                                                             #
###############################################################

@app.route("/ivm/")
def ivm():
        cursor = None
        dbConn = None

        try:
                # get current page
                page = request.args.get("page")
                if (page == None):
                        page = 0

                page = int(page)
                page_offset = page * TABLE_SIZE
                query = f"SELECT * FROM {IVM_TABLE} OFFSET {page_offset} FETCH FIRST {TABLE_SIZE} ROWS ONLY"
                dbConn, cursor = dbConnect()
                cursor.execute(query)

                return render_template("ivmMain.html", cursor=cursor, ivm=IVM_PATH, app=APP_PATH, page=page)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=IVM_PATH)
        finally:
                cursor.close()
                dbConn.close()


@app.route("/ivm/view/")
def ivmView():
        cursor = None
        dbConn = None

        try:
                # connect to the database
                dbConn, cursor = dbConnect()
                serial_number = request.args.get("serial_num")
                supplier = request.args.get("supplier")

                # check if the ivm exists
                query = f"SELECT * FROM {IVM_TABLE} WHERE {SERIAL_NUMBER} = %s AND {SUPPLIER} = %s;"
                cursor.execute(query, (serial_number, supplier))

                if (cursor.rowcount == 0):
                        title = "Error"
                        text = f"The IVM \'{ serial_number } : { supplier }\', does not exist"
                        return render_template("prompt.html", title=title, text=text, return_to=IVM_PATH)

                # get all replenishment events associated with this ivm
                query = f"SELECT * FROM {REPLENISHMENT_TABLE} WHERE {SERIAL_NUMBER} = %s AND {SUPPLIER} = %s;"
                cursor.execute(query, (serial_number, supplier))
                replenishment_events = copyRecords(cursor)
                
                # get the total number of replenished products for all products 
                query= f"SELECT {EAN}, SUM({UNITS}) FROM {REPLENISHMENT_TABLE} WHERE {SERIAL_NUMBER} = %s AND {SUPPLIER} = %s GROUP BY {EAN};"
                cursor.execute(query, (serial_number, supplier))
                unit_sum = copyRecords(cursor)

                return render_template("ivmView.html", replenishment_events=replenishment_events, unit_sum=unit_sum, serial_num=serial_number, supplier=supplier, ivm=IVM_PATH)
        except Exception as e:
                title = "Error"
                text = "The following error occurred \'" + str(e) + "\'"
                return render_template("prompt.html", title=title, text=text, return_to=IVM_PATH)
        finally:
                cursor.close()
                dbConn.close()


CGIHandler().run(app)