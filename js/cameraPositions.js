//We assume m_pos exists in markers
function move_camera_marker(m_pos,lat_str,lng_str,rotation){
    zoomUpdateCameras(m_pos,rotation);
    //this zoomupdate is for drawing the icon with correct size
	
    let lat_float=parseFloat(lat_str);
    let lng_float=parseFloat(lng_str);
    
    let position_dot=new google.maps.LatLng(lat_float, lng_float);

    //let dummyvar = (typeof Function.prototype === "function"); 
    //await sleep(10); //sleep 10ms
    if(position_dot===undefined){
          console.log("POS IS UNDEFINED");
    }
    if(cameraPositions.length<=m_pos){
	        console.log("length problem for cameras");    
    }
    if(cameraPositions[m_pos]===undefined){
	        console.log("mpos is undefined");    
    }
	
    cameraPositions[m_pos].setPosition( position_dot);
    //cameraPositions[m_pos].setOpacity(0.5);
    
    cameraPositions[m_pos].setMap(map);       
}

function cameraUpdate(){
	$.ajax(ajaxSettingsCamera).done(ajaxdoneCamera).fail(ajaxfailCamera);return;	
}

function ajaxdoneCamera(receivedMessage) {
      if(receivedMessage === undefined){
            cameraCoords = [];
      }else{
            if(receivedMessage['message'] !== undefined){
                  console.error("Camera ajax message is "+receivedMessage['message']);
                  cameraCoords = [];
                  cameraCoords.length = 0;
            }else{
                  cameraCoords = JSON.parse(receivedMessage['cameraCoordinates']);
            }	
      }
}

function ajaxfailCamera(xhr, status, errorThrown) {
    //console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
    //console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
            // API Gateway gave up.  Let's retry.
            if( ajaxSettingsCamera.retries-- > 0 ){
                  setTimeout(cameraUpdate, 1000);
            }else{
                  console.log("Retried but no luck for camera coordinates");
            }  
    } else {
          //defaultFailFunction(xhr, textStatus, errorThrown);
          console.log("Everything is done for camera");
          // or you could call dfd.reject if your users call $.ajax().fail()
    }
	
    cameraCoords = [];
    cameraCoords.length = 0;	    
}
function zoomUpdateCameras(m_pos,rotation){
    let zoom_level = map.getZoom(); 
    let img_size=zoom_level/400;
    
  /*  
    var icon_dict={"scaledSize":new google.maps.Size(img_size, img_size), "anchor":new google.maps.Point(img_size/2, img_size/2),
    "url":redIconImage,};
*/	
    
   
    var icon_dict={
          rotation:parseInt(rotation),
	  path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          //path:'M17 482 c-14 -16 -17 -43 -17 -164 0 -128 2 -147 18 -161 16 -15 47 -17 225 -17 201 0 206 0 221 22 9 12 16 32 16 45 l0 22 57 -20 c68 -23 68 -23 87 -3 23 22 23 206 0 228 -19 20 -19 20 -87 -3 l-57 -20 0 22 c0 13 -7 33 -16 45 -15 22 -20 22 -223 22 -189 0 -209 -2 -224 -18z m414 -12 c17 -10 19 -22 19 -148 0 -94 -4 -142 -12 -150 -17 -17 -379 -17 -396 0 -8 8 -12 56 -12 150 0 120 2 138 18 147 23 14 357 14 383 1z m179 -151 l0 -101 -27 5 c-16 3 -45 13 -65 21 -38 16 -38 17 -38 75 l0 60 53 20 c28 11 58 20 65 20 9 1 12 -26 12 -100z',	    
          //path:'m10.39883,614.35c-8.56374,-16.57778 -10.39883,-44.55278 -10.39883,-169.92222c0,-132.62222 1.22339,-152.30833 11.01053,-166.81389c9.78713,-15.54167 28.74971,-17.61389 137.63158,-17.61389c122.95088,0 126.00936,0 135.1848,22.79444c5.50526,12.43333 9.78713,33.15556 9.78713,46.625l0,22.79444l34.86667,-20.72222c41.59532,-23.83056 41.59532,-23.83056 53.21755,-3.10833c14.06901,22.79444 14.06901,213.43889 0,236.23333c-11.62222,20.72222 -11.62222,20.72222 -53.21755,-3.10833l-34.86667,-20.72222l0,22.79444c0,13.46944 -4.28187,34.19167 -9.78713,46.625c-9.17544,22.79444 -12.23392,22.79444 -136.40819,22.79444c-115.61053,0 -127.84445,-2.07222 -137.01989,-18.65zm253.24211,-12.43333c10.39883,-10.36111 11.62222,-22.79444 11.62222,-153.34445c0,-97.39444 -2.44678,-147.12778 -7.34035,-155.41667c-10.39883,-17.61389 -231.83275,-17.61389 -242.23158,0c-4.89357,8.28889 -7.34035,58.02222 -7.34035,155.41667c0,124.33333 1.22339,142.98333 11.01053,152.30833c14.06901,14.50556 218.37544,14.50556 234.27954,1.03611zm109.49357,-156.45278l0,-104.64722l-16.51579,5.18056c-9.78713,3.10833 -27.52632,13.46944 -39.76023,21.75833c-23.24444,16.57778 -23.24444,17.61389 -23.24444,77.70833l0,62.16667l32.41988,20.72222c17.12749,11.39722 35.47836,20.72222 39.76023,20.72222c5.50526,1.03611 7.34035,-26.93889 7.34035,-103.61111z',
	  scale: 5-(10/zoom_level), // 0.25/img_size,
          fillColor: '#000000',
          fillOpacity: .6,
          anchor: new google.maps.Point(0, img_size/(2)),
          strokeWeight: 0,    
    };
    
	
    if(cameraPositions[m_pos] === undefined){
          alert("a marker is undefined markers size"+markers.length+" position "+m_pos+" dict_size "+markers_dict.length);
          console.log(icon_dict);
    }
    if(icon_dict === undefined){
          alert("dict icon is undefined markers size"+markers.length+" position "+m_pos+" dict_size "+markers_dict.length);
          console.log(icon_dict);
    }
    cameraPositions[m_pos].setIcon(icon_dict);

}
