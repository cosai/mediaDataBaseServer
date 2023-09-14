function ajaxdonealldata(receivedMessage) {
    if (receivedMessage === undefined) {
        alldata = [];
        alldata.length = 0;
    } else {
        alldata = receivedMessage;	
    } //end of else if
}

function ajaxfailalldata(xhr, status, errorThrown) {
    if (xhr && xhr.readyState === 0 && xhr.status === 0 && xhr.statusText === "error") {
        // API Gateway gave up.  Let's retry.
        if (ajaxSettingsalldata.retries-- > 0) {
            setTimeout(alldataUpdate, 1000);
        } else {
            //console.log("Retried but no luck for camera exits");
        }
    } else {
        //defaultFailFunction(xhr, textStatus, errorThrown);
        //console.log("Everything is done for exists");
        // or you could call dfd.reject if your users call $.ajax().fail()
    }
    alldata = []
    alldata.length = 0;
}

function alldataUpdate() {
    $.ajax(ajaxSettingsalldata).done(ajaxdonealldata).fail(ajaxfailalldata);
    return;
}
