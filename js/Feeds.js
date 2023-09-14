function getInfoViewInside(vcuip) {
    let camurl1="http://admin:curruS101@"+vcuip+":8001/cgi-bin/mjpg/video.cgi?channel=0&subtype=1";	
    let camurl2="http://admin:curruS101@"+vcuip+":8002/cgi-bin/mjpg/video.cgi?channel=0&subtype=1";	
    
    let cam1frame="<iframe src=\""+camurl1+"\" style=\"height: 320px;width: 320px;\"></iframe>";
    let cam2frame="<iframe src=\""+camurl2+"\" style=\"height: 320px;width: 320px;\"></iframe>";  
    return cam1frame+cam2frame;
}

function feedsUpdate(){
     ajaxSettingsfeeds.url=ajaxSettingsfeeds.baseurl+"/"+"IP_"+currentVCUname;
     $.ajax(ajaxSettingsfeeds).done(ajaxdonefeeds).fail(ajaxfailfeeds);
}

function ajaxdonefeeds(receivedMessage) {
    if(receivedMessage === undefined){
          vcuIPs[currentVCUname]= "";
    }else{
        if(receivedMessage["IP_"+currentVCUname] === undefined ){
		        console.error("feeds ajax message is "+receivedMessage["IP_"+currentVCUname]);
		        vcuIPs[currentVCUname]= "";
        }else{
		        vcuIPs[currentVCUname]=receivedMessage["IP_"+currentVCUname];	
        }//end of else if	
   }//end of else if
}

function ajaxfailfeeds(xhr, status, errorThrown) {
    //console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
    //console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
            // API Gateway gave up.  Let's retry.
            if( ajaxSettingsfeeds.retries-- > 0 ){
                  setTimeout(feedsUpdate, 1000);
            }else{
                  console.log("Retried but no luck for camera coordinates");
            }  
    } else {
          //defaultFailFunction(xhr, textStatus, errorThrown);
          console.log("Everything is done for feeds");
          // or you could call dfd.reject if your users call $.ajax().fail()
    }
    vcuIPs[currentVCUname]= "";    
}
