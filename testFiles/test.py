import requests
import json
import base64
from PIL import Image
import io, base64
from io import BytesIO
import sys
import os
from flask import jsonify

websitename='http://1.2.3.4:5000'

#those functions are for storing files/images  or UPLOADING to a web page with POST request  
def keys(itemname="*"):
    res = requests.get(websitename+'/keys/'+itemname)
    if res.ok:
        return(res.json())
    else:
        print(res.status_code)
        print(res.text)
        return None

# itemid : key
# imagefilepath : file to be saved under key (should be image file)
def setFile(itemid:str,imagefilepath:str):
    image_name=imagefilepath
    with open(image_name, 'rb') as f:
        r = requests.post(websitename+'/uploadFile/'+itemid, files={itemid: f})
           
# those functions are for retrieveing files/images
# the file is shown as base64. That file is saved as image with name itemid.ext
# the itemid will be the name of the file
# THIS IS USING BASE 64
def get_file2(self, itemid: str):
    res = requests.get(self.websitename + '/getFile/' + itemid)
    file_content = res.content.decode('utf8')
    newfilecontent = file_content[file_content.find(',') + 1:-2]
    # file extension is between / and ; ex: <img src="data,type:img/png;dd4tf862Xfmg7dsX">
    fileExtension = file_content[file_content.find("/") + 1:file_content.find(";")]
    try:
        imgdata = base64.b64decode(newfilecontent)
        # filename is the new file name
        filename = itemid + '.' + fileExtension  # Filename will be  itemid
        with open(filename, 'wb') as f:
            f.write(imgdata)
        return os.path.abspath(filename)
    except Exception as e:
        print(str(e))
        return None

# This function is to download an image from a request
# itemid : key value
# downloadedFileName : name of file to be saved (the extension will be added automatically) 
# it will return the absolute path of the downloaded file
def getFile(itemid:str,downloadedFileName:str)->str:
    res = requests.get(websitename + '/getFile/' + itemid)
    extension = res.headers['Content-Type'].replace("image/","")
    createdFileName=downloadedFileName+"."+extension
    file = open(createdFileName, "wb")  ## Creates the file for image
    file.write(res.content)  ## Saves file content
    savedFilePath=os.path.abspath(createdFileName)
    file.close()
    return str(savedFilePath)

#added Object should be a dictionary
def setValue(itemid:str,addedObject):
    ###setting value
    res = requests.post(websitename+'/set/'+itemid, json=addedObject)
    if res.ok:
        print(res.json())
    else:
        print(res.status_code)
        print(res.text)

# {itemdict is a dictionary. each key holds an object to be stored
def setValueBatch(itemidDict):
    res = requests.post(websitename+'/setBatch/', json=itemidDict)
    if res.ok:
        return res.json()
    else:
        print(res.status_code)
        print(res.text)
        return None
    
def getValueBatch(itemids:list):
    res = requests.post(websitename+'/getBatch/', json=itemids)  
    if res.ok:
        return res.json()
    else:
        print(res.status_code)
        print(res.text)
        return None
 
## getting value
def getValue(itemid:str):
    res = requests.get(websitename+'/get/'+itemid)
    print(res.json())
    if res.ok:
        extractedObj = res.json()
        replyf = extractedObj.get("message",None)
        if  replyf is not None and  replyf =="Not in cache":
            return None
        
        return extractedObj
    else:
        print(res.status_code)
        arr=json.loads(res.text)
        errorMessage=arr['message']
        print(errorMessage)
        return None

## destroying all values
def deleteAll():
    res = requests.get(websitename+'/destroyAllRecords')
    if res.ok:
        print("OK")
        #jss=res.json()
        print(res.text)
    else:
        print("NOT OK")
        print(res.status_code)
        print(res.text)

def deletefile(fname:str):
    #checking if file exist or not
    if(os.path.isfile(fname)):
        #os.remove() function to remove the file
        os.remove(fname)
        #Printing the confirmation message of deletion
        print("File Deleted successfully")
        return True
    else:
        print("File does not exist")
        return False
        #Showing the message instead of throwig an error

#deleting a key
def delete(itemid:str):
    res = requests.get(websitename+'/get/'+itemid)
    if res.ok:
        jss=res.json()
        addedval=jss[itemid]
        if addedval != "Not in cache":
            if isinstance(addedval,str) and ( ".png" in addedval or ".jpeg" in addedval or ".webp" in addedval or "jpg" in addedval):
                if not deletefile(addedval):
                     print("File can not be deleted")
            else:
                print("not str")
                #now deleting the entry
                res = requests.get(websitename+'/delete/'+itemid)
                if res.ok:
                    print("deleted successfully")
                    jss=res.json()
                else:
                    print("NOT OK")
                    print(res.status_code)
                    arr=json.loads(res.text)
                    print(arr['message'])
    else:
        print("NOT OK")
        print(res.status_code)
        print(res.text)

if __name__ == "__main__":
    safa()
    item1="currus1"
    addedObject1={"name":"company1"}
    item2="currus2"
    addedObject2={"name":"company2"}
    item3="currus3"
    addedObject3={"name":"company3"}
    
    
    print("startedBatching")
    listtosend={}
    listtosend[item1]=addedObject1
    listtosend[item2]=addedObject2
    listtosend[item3]=addedObject3

    returned=setValueBatch(listtosend)
    if returned is None:
        print("ERROR")
    else:
        print(returned)
    
    returnedlist=getValueBatch(json.dumps([item1,item2,item3]))
    print("Returned Elements: ")
    if returnedlist:
        for el in returnedlist.keys():
            if el:
                print(el,returnedlist[el],"\ntype of stored element in dictionary key is:",type(returnedlist[el]) )
            else:
                print("None")
    else:
        print("NONE GAVE")
    
    setValue("test_item","{another}")
    as1=None
    as1=getValue("test_item")
    print(as1)
    delete("test_item")
    as1=getValue("test_item")
    print("This should be none",as1)
    for el in keys("sa*"):
        print(el)
    res_returned=keys("dsdsdadsad")
    if len(res_returned) == 0:
        print("Empty dictionary ")
    """
    deleteAll()
   
    imagefilepath="temp.webp"
    setFile(item1,imagefilepath)
    downloadedFilePath=getFile(item1,"Downloaded") # the file will be saved as item1.ext
    delete(item1)
    print(downloadedFilePath,"path")
    """
