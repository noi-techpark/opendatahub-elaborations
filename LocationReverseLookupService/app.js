const endpoint = "http://127.0.0.1:8080/writer/json/stationsWithoutMunicipality";
const sendUrl = "http://127.0.0.1:8080/writer/json/patchStations";
const logger = require('winston');
logger.level='info';
const osmReverseLookupUrl = "http://nominatim.openstreetmap.org/reverse";
var request = require("request")
exports.handler = (event, context, callback) => {
    var data = init();
    callback(null, data);
};
exports.getInputData = function(){
	return new Promise(function(resolve,reject){
		request.get({
			url: endpoint,
		    	json: true
		}, function (error, response, body) {
			logger.info(body);
    			if (!error && response.statusCode === 200)
				      resolve(body);
		    	else
				      reject(error);
		});
	});
}
var getTownNameByCoordinate = function(longitude,latitude){
	return new Promise(function(resolve, reject){
		if (!longitude || !latitude)
			reject("required request parameters not provided");
		request.get({
    			url: osmReverseLookupUrl,
			headers:{
				referer:'IDM-Suedtirol'
			},
		    	json: true,
			qs:{
				format: "jsonv2",
				lon: longitude,
				lat: latitude
			}
		}, function (error, response, body) {
	 		if (!error && response.statusCode === 200)
				resolve(body);
	    		else
				reject(error);
		});

	});
}
var send = function(mappings){
	request.post({
		url:sendUrl,
		json:true,
		body:mappings
	},function(error,response,body){
		if (!error && response.statusCode === 200)
			logger.debug("Data sent");
	    	else
			logger.debug("post failed with error" + error);
	});
}
function init(){
	exports.getInputData().then(function(stations){
    var totalLength = stations.length;
    logger.info("Retrieved " + totalLength + " objects");
    logger.info("Start to retrieve municipality of objects");
		var objWithCoordinates = [];
		recursiveRetrival();
		function recursiveRetrival(){
      logger.info("Found "+ objWithCoordinates.length +" of " + totalLength);
			if (stations.length === 0){
        logger.info("About to send "+objWithCoordinates.length +" objects");
				send(objWithCoordinates);
				return objWithCoordinates;
			}
			var station = stations.pop();
			getTownNameByCoordinate(station.longitude, station.latitude)
			.then(function(jR){
				var address = jR.address;
        if (address)
				    objWithCoordinates.push({municipality:address.city||address.town||address.village||address.hamlet,id:station.id,"_t":"it.bz.idm.bdp.dto.StationDto",stationType:station.stationType});
        else {
            logger.info("Could not get address info of object with id" + station.id);
        }
			}).then(function(){
				setTimeout(recursiveRetrival,1000);
			}).catch(function(err){console.log(err);setTimeout(recursiveRetrival,1000)});
		}
	}).catch(err => console.log(err));
}


init();
