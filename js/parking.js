function ajaxdonemqtttopic(receivedMessage) {
    if (receivedMessage === undefined) {
        console.error("undefined mqtopic");
    } else {
        if (receivedMessage['message'] !== undefined) {
            if(receivedMessage['message'].includes("SUCCESS")){
                console.log("SUCCESS on change mqtt topic");   
            }
        } else {
            console.error("undefined message on mqtt topic change"); 
        }
    }
}

function ajaxfailmqtttopic(xhr, status, errorThrown) {

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
        // API Gateway gave up.  Let's retry.
        if (ajaxSettingsmqtttopic.retries-- > 0) {
            setTimeout(mqtttopicUpdate, 1000);
        } else {
            ;
            //console.log("Retried but no luck for parking");
        }
    } else {
        ;
        //defaultFailFunction(xhr, textStatus, errorThrown);
        //console.log("Everything is done for parking");
        // or you could call dfd.reject if your users call $.ajax().fail()
    }
    //make end reuslt for mqtttopic
}

function mqtttopicUpdate() {
    $.ajax(ajaxSettingsmqtttopic).done(ajaxdonemqtttopic).fail(ajaxfailmqtttopic);
    return;
}

////////////////////////////////////////////////////////////////////





function ajaxdoneParking(receivedMessage) {
    if (receivedMessage === undefined) {
        parkingLocations=receivedMessage;
    } else {
        if (receivedMessage['message'] !== undefined) {
            console.log("message is "+receivedMessage['message']);
            parkingLocations= [];
            parkingLocations.length = 0;
        } else {
            try{ 
                parkingLocations = receivedMessage;
            } catch(e) { 
                console.error("Caught: " + e.message);
                console.error(receivedMessage["parkinglocations"]);
            }
            
        }
    }
}

function ajaxfailParking(xhr, status, errorThrown) {
    //console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
    //console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
        // API Gateway gave up.  Let's retry.
        if (ajaxSettingsparking.retries-- > 0) {
            setTimeout(parkingLocationsUpdate, 1000);
        } else {
            ;
            //console.log("Retried but no luck for parking");
        }
    } else {
        ;
        //defaultFailFunction(xhr, textStatus, errorThrown);
        //console.log("Everything is done for parking");
        // or you could call dfd.reject if your users call $.ajax().fail()
    }
    parkingLocations = [];
    parkingLocations.length = 0;
}

function parkingLocationsUpdate() {
    $.ajax(ajaxSettingsparking).done(ajaxdoneParking).fail(ajaxfailParking);
    return;
}

function pnpoly(nvert, vertx,verty,testx, testy)
{
  var i, j, c = 0;
  for (i = 0, j = nvert-1; i < nvert; j = i++) {
   if ( ((verty[i]>testy) != (verty[j]>testy)) && (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) )
        c = !c;
   }
    return c;
}

//checks if lat and lon are inside a rectangle of
// topleft and bottom right corners
function checkCoord(arr, lat, lon){
    var longitudes=[arr[0][1],arr[1][1],arr[2][1],arr[3][1]];
    var latitudes=[arr[0][0],arr[1][0],arr[2][0],arr[3][0]];
    var retval=pnpoly(4,longitudes, latitudes, lon, lat);
    if(retval ==1){
        return true;
    }
    return false;
}
