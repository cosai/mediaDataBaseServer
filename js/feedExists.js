

function getInfoViewInside(cameraname) {
    //cameraname=cameraname+persp	
    perspframe="<iframe src=\"../video_feed/"+cameraname+"persp"+"\" style=\"height: 320px;width: 320px;\"></iframe>";
    bevframe="<iframe src=\"../video_feed/"+cameraname+"bev"+"\" style=\"height: 320px;width: 320px;\"></iframe>";  
    //bev  cameraname=cameraname+bev
    //cameraname=cameraname.replace("persp","");cameraname=cameraname.replace("bev","")
    return perspframe+bevframe;
}


function ArrayIncludes(arr1,elem){
    for(var i=0;i<arr1.length;i++){
		    if(arr1[i].includes(elem))return true;
	  }
	  return false;
}
 
function existsUpdate(name){
    $.ajax(ajaxSettingsExists).done(ajaxdoneexists).fail(ajaxfailexists);return;	
}

function ajaxdoneexists(receivedMessage) {
    if(receivedMessage === undefined){
          channelExists = [];
	        channelExists.length = 0;
    }else{
        if(receivedMessage['exists'] === undefined ){
		        console.error("Camera ajax message is "+receivedMessage['exists']);
		        channelExists = [];
	          channelExists.length = 0;
        }else{
		        channelExists=receivedMessage['exists'];	
        }//end of else if	
   }//end of else if
}

function ajaxfailexists(xhr, status, errorThrown) {
    //console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
    //console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
            // API Gateway gave up.  Let's retry.
            if( ajaxSettingsExists.retries-- > 0 ){
                  setTimeout(existsUpdate, 1000);
            }else{
                  console.log("Retried but no luck for camera coordinates");
            }  
    } else {
          //defaultFailFunction(xhr, textStatus, errorThrown);
          console.log("Everything is done for exists");
          // or you could call dfd.reject if your users call $.ajax().fail()
    }
    channelExists=[]
    channelExists.length = 0;	    
}

