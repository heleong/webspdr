from pymongo import MongoClient

def find_fuye199_sold_units(server = "mongodb://localhost:27017/", database = "realestate", collection = "fuye199", data = None):
    client = MongoClient(server)
    
    # Test the connection
    try:
        client.server_info()
        print("Successfully connected to MongoDB!")
        db = client[database]
        c = db[collection]
        doc = c.find().sort('timestamp', -1).limit(1).next() 
        data = {}
        count_r = 0
        count_y = 0
        for b in doc["data"]["buildings"]:
                #print("--------------->building_name",b["building_name"], "-------->units", b["units"])
                for u in b["units"]:
                    if u["status_class"] in ["_red_bg"]:
                        count_r += 1
                        data[b["building_name"]+u["unit_info"]] = u["status"]
                    if u["status_class"] in ["_yellow_bg"]:
                        count_y += 1
                        data[b["building_name"]+u["unit_info"]] = u["status"]
        data["timestamp"] = doc["timestamp"]
        data["已登记"] = count_r
        data["已签"] = count_y
        return data
    except Exception as e:  
        print(f"Failed to connect to MongoDB: {e}")
        return False
    finally:
        client.close()

def find_fuye199_status_changed(server = "mongodb://localhost:27017/", database = "realestate", collection = "fuye199", data = None):
    client = MongoClient(server)
    
    # Test the connection
    try:
        client.server_info()
        print("Successfully connected to MongoDB!")
        db = client[database]
        c = db[collection]
        cursor = c.find().sort('timestamp', -1) # cursor
        data = {}
        for d in cursor:
            #print("--------------->timestamp",d["timestamp"])
            for b in d["data"]["buildings"]:
                #print("--------------->building_name",b["building_name"], "-------->units", b["units"])
                for u in b["units"]:
                    if "status_changed" in u.keys():
                        #print("--------------->unit_info",u["unit_info"], "------>status", u["status"], "------>status_changed", u["status_changed"])
                        if u["status_changed"] == 1:
                            data[b["building_name"]+u["unit_info"]+str(d["timestamp"])] = u["status"]
        return data
    except Exception as e:  
        print(f"Failed to connect to MongoDB: {e}")
        return False
    finally:
        client.close()

def update_fuye199_status(server = "mongodb://localhost:27017/", database = "realestate", collection = "fuye199", data = None):
    client = MongoClient(server)
    
    # Test the connection
    try:
        client.server_info()
        print("Successfully connected to MongoDB!")
        db = client[database]
        c = db[collection]
        if data is not None:
            # TODO: update the status of the data
            pass
        else:
            print("Traverse the data and update the status ...")
            docs = list(c.find().sort('timestamp', 1)) 
            for n in range(len(docs)-1):
                doc = docs[n]
                doc_next = docs[n+1]
                #print("--------------->Compare n and n+1","n: ",n," n+1: ",n+1)
                #print("--------------->doc[n]",doc["timestamp"])
                #print("--------------->doc_next",doc_next["timestamp"])
                if doc_next:
                    i = 0
                    while i < len(doc["data"]["buildings"]):
                        j = 0
                        while j < len(doc_next["data"]["buildings"]):
                            if doc["data"]["buildings"][i]["building_name"] == doc_next["data"]["buildings"][j]["building_name"]:
                                break
                            else:
                                j += 1
                        m = 0
                        while m < len(doc["data"]["buildings"][i]["units"]):
                            if doc["data"]["buildings"][i]["units"][m]["unit_info"] != doc_next["data"]["buildings"][j]["units"][m]["unit_info"]:
                                raise Exception("Unit info is not the same")
                            if doc["data"]["buildings"][i]["units"][m]["status_class"] == doc_next["data"]["buildings"][j]["units"][m]["status_class"]:
                                doc_next["data"]["buildings"][j]["units"][m]["status_changed"] = 0
                            else:
                                doc_next["data"]["buildings"][j]["units"][m]["status_changed"] = 1
                                print("--------------->Compare n and n+1","n: ",n," n+1: ",n+1)
                                print("--------------->doc[n]",doc["timestamp"], "building:", doc["data"]["buildings"][i]["building_name"], "unit:", doc["data"]["buildings"][i]["units"][m]["unit_info"], "--->", doc["data"]["buildings"][i]["units"][m]["status_class"])
                                print("--------------->doc_next",doc_next["timestamp"], "building:", doc_next["data"]["buildings"][j]["building_name"], "unit:", doc_next["data"]["buildings"][j]["units"][m]["unit_info"], "--->", doc_next["data"]["buildings"][j]["units"][m]["status_class"])
                            m += 1
                            c.update_one({"_id": doc_next["_id"]}, {"$set": {"data": doc_next["data"]}})
                        i += 1
                else:
                    break
            return True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    update_fuye199_status()
    print("--------------------------------")
    print("status changed data:")
    print("--------------------------------")
    print(find_fuye199_status_changed())
    #print("--------------------------------")
    #print("sold units data:")
    #print("--------------------------------")
    #print(find_fuye199_sold_units())