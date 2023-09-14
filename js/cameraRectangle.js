//fourpoints should be an array of dictionaries
// each dictionary should have lat and lng values
function drawPolygon(fourpoints,positionPolygon){
	//the last point should be readded to the array so that
	// the polygon will be a closed shape
	/*const polygonCoords = [
	{ lat: 25.774, lng: -80.19 },	{ lat: 18.466, lng: -66.118 },	{ lat: 32.321, lng: -64.757 },	
	{ lat: 32.311, lng: -64.5 },	{ lat: 25.774, lng: -80.19 }, ];  */
	//polygonObjects[positionPolygon].setMap(null);
	//polygonObjects[positionPolygon]=null;
	const polygonCoords = [fourpoints[0],fourpoints[1],fourpoints[2],fourpoints[3],fourpoints[0],];
	// Construct the polygon.
	const camerapolygon = new google.maps.Polygon({
		paths: polygonCoords,
		strokeColor: "#00008F",
		strokeOpacity: 0.003,
		strokeWeight: 2,
		fillColor: "#00008F",
		fillOpacity: 0.003,
	});

	camerapolygon.setMap(map);
	polygonObjects[positionPolygon]=camerapolygon;
	
}

function drawCircle(givenCenter,radiusgiven){
	const cityCircle = new google.maps.Circle({
		strokeColor: "#FF0000",
		strokeOpacity: 0.005,
		strokeWeight: 1,
		fillColor: "#FF0000",
		fillOpacity: 0.005,
		map,
		center: givenCenter,
		radius: radiusgiven,
	});		
}


function ajaxdoneRectangle(receivedMessage) {
	if(receivedMessage === undefined){
		cameraRectangleCoords = [];
	}else{
		if(receivedMessage['message'] !== undefined){
		    console.error("Rectangle error "+receivedMessage['message']);
		    cameraRectangleCoords = [];
		    cameraRectangleCoords.length = 0;
		}else{
		    cameraRectangleCoords = JSON.parse(receivedMessage['cameraRectangleCoordinates']);
		}	
	}
}

function ajaxfailRectangle(xhr, status, errorThrown) {
	//console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
	//console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);
	    
	if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
	        // API Gateway gave up.  Let's retry.
	        if( ajaxSettingsRectangle.retries-- > 0 ){
			setTimeout(cameraRectangleUpdate, 1000);
		}else{
			console.log("Retried but no luck for Rectangle");
		}  
	} else {
	    	//defaultFailFunction(xhr, textStatus, errorThrown);
	    	console.log("Everything is done for camera Rectangle");
		// or you could call dfd.reject if your users call $.ajax().fail()
	}
	
	cameraRectangleCoords = [];
	cameraRectangleCoords.length = 0;	    
}

function cameraRectangleUpdate(){
	$.ajax(ajaxSettingsRectangle).done(ajaxdoneRectangle).fail(ajaxfailRectangle);return;
}
