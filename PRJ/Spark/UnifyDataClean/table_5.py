from UnifyDataClean.tools import getReadDB, getWriteDB, roleDefine, getMap

import time
db, cursor = getWriteDB()


def getlane(cursor):
    dic = {}
    lanes = ["BOTTOM", "TOPSOLO", "MIDDLE", "JUNGLE", "SUPPORT"]
    cidName = getMap()
    for lane in lanes:
        col = "role"
        sql = "SELECT * FROM table_1 WHERE {} = '{}';".format(col, lane)
        print(sql)
        cursor.execute(sql)
        tmp = cursor.fetchall()


        for item in map(lambda x: {"cid": x[0], "appear": float(x[2]), "role": x[3]},tmp):
            if item["cid"] in dic:
                if dic[item["cid"]]["appear"] < item['appear']:
                    dic[item["cid"]] = item
                else:
                    pass
            else:
                dic[item["cid"]] = item
    return dic
dic = getlane(cursor)

def map_1(row):
    cid = row["cid"]
    define = dic[cid]["role"] if cid != "" else ""
    win = 1 if row['win'] == "True" else 0
    kills = 0 if row["totalkill"] == "" else int(row["totalkill"])
    killed = 0 if row["totalkilled"] == "" else int(row["totalkilled"])
    damage =0 if row["damage"] == "" else int(row["damage"])
    damaged = 0 if row["damagetaken"] == "" else int(row["damagetaken"])
    heal =0 if row["heal"] == "" else  int(row["heal"])
    assist = 0 if row["totalsupport"] == "" else int(row["totalsupport"])

    return ((cid, define), (win, 1, kills, killed, damage, damaged, heal, assist))
def map_2(row):
    define = roleDefine(row["role"], row["lane"])
    if define == '-1':
        define = ""
    return (define, 1)
def dataClean(rdd0):

    rdd1 = rdd0.map(map_1)
    rdd2 = rdd1.reduceByKey(lambda x, y:(x[0]+y[0], x[1]+y[1], x[2]+y[2], x[3]+y[3], x[4]+y[4], y[5]+x[5], y[6]+x[6], x[7]+y[7]))
    l1  =  rdd2.collect()

    rdd3 = rdd0.map(map_2)
    rdd4 = rdd3.reduceByKey(lambda x, y: x+y)
    l2 = rdd4.collect()
    return l1,l2

def write(l, l2, db, cursor):
    dic = {}
    for item in l2:
        dic[item[0]] = item[1]
    for i in range(len(list(l))):
        row = l[i]
        cursor.execute("INSERT INTO table_5 (cid, role, win, appear, kills, killed, heal, damage, damaged, assist ) \
                        VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                        row[0][0], row[0][1], row[1][0]/row[1][1], row[1][1]/dic[row[0][1]], row[1][2]/row[1][1], row[1][3]/row[1][1], row[1][4]/row[1][1], row[1][5]/row[1][1], row[1][6]/row[1][1], row[1][7]/row[1][1]))
    db.commit()
    db.close()
def app():

    rdd = getReadDB(table="table_dirty")
    l , l2= dataClean(rdd)
    write(l,l2, db, cursor)
if __name__ == '__main__':
    app()

