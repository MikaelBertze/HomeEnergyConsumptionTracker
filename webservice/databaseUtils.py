import MySQLdb
from scipy.interpolate import interp1d
from scipy import arange, array, exp


databaseUser = ""
databasePass = ""
databaseDb = ""


def connect():
    return MySQLdb.connect(user=databaseUser, passwd=databasePass,db=databaseDb)


def insert_many(query, data):
    try:
        db = connect()
        c=db.cursor()
        c.executemany(query, data)
        db.commit()
        db.close()
    except Exception as e:
        print "SQL error: " + e.message


def query_for_data(query):
    rows = []
    try:
        db = connect()
        c=db.cursor()
        c.execute(query)
        rows = c.fetchall()
        db.commit()
        db.close()
    except:
        print "SQL error"
    return rows


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def extrap1d(interpolator):
    xs = interpolator.x
    ys = interpolator.y

    def pointwise(x):
        if x < xs[0]:
            return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
        elif x > xs[-1]:
            return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
        else:
            return interpolator(x)


    def ufunclike(xs):
        return array(map(pointwise, array(xs)))

    return ufunclike