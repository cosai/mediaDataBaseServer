function ajaxdoneSubscribe(receivedMessage) {
    if (receivedMessage === undefined) {
        prev_marker_dict = markers_dict;
        markers_dict = receivedMessage;
        numberofmarkers = markers_dict.length;
    } else {
        if (receivedMessage['message'] !== undefined) {
            console.log(receivedMessage['message']);
            markers_dict = [];
            markers_dict.length = 0;
            numberofmarkers = 0;
        } else {
            prev_marker_dict = markers_dict;
            markers_dict = receivedMessage;
            numberofmarkers = markers_dict.length;
        }
    }
}

function ajaxfailSubscribe(xhr, status, errorThrown) {
    //console.log("Caught error: " + JSON.stringify(xhr) + ", textStatus: " + status + ", errorThrown: " + errorThrown);
    //console.log("Ready State: " + xhr.readyState + ", Stat: " + xhr.status + ", statusText: " + xhr.statusText);

    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
        // API Gateway gave up.  Let's retry.
        if (ajaxSettingsSubscribe.retries-- > 0) {
            setTimeout(subscribeUpdate, 1000);
        } else {
            //console.log("Retried but no luck");
        }
    } else {
        //defaultFailFunction(xhr, textStatus, errorThrown);
        //console.log("Everything is done for subscription");
        // or you could call dfd.reject if your users call $.ajax().fail()
    }
    markers_dict = [];
    markers_dict.length = 0;
    numberofmarkers = 0;
}

function subscribeUpdate() {
    $.ajax(ajaxSettingsSubscribe).done(ajaxdoneSubscribe).fail(ajaxfailSubscribe);
    return;
}

function move_marker(m_pos, lat_str, lng_str) {
    zoomUpdate(m_pos);
    //this zoomupdate is for drawing the icon with correct size

    let lat_float = parseFloat(lat_str);
    let lng_float = parseFloat(lng_str);

    let position_dot = new google.maps.LatLng(lat_float, lng_float);

    //let dummyvar = (typeof Function.prototype === "function"); 
    //await sleep(10); //sleep 10ms
    if (position_dot === undefined) {
        console.log("POS IS UNDEFINED");
    }
    if (markers.length <= m_pos) {
        console.log("length problem for markers");
    }
    if (markers[m_pos] === undefined) {
        console.log("mpos is undefined for markers");
    }

    markers[m_pos].setPosition(position_dot);
    markers[m_pos].setOpacity(0.5);

    //ifs were here    
    markers[m_pos].setMap(map);

}
