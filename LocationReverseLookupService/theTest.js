// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

var assert = require('assert');
var bdpMuni = require('./app.js');
var chai = require('chai');  
var chaiAsPromised = require("chai-as-promised");
chai.use(chaiAsPromised);
var expect = chai.expect;
describe('testingAPI',function(){
	it('should provide some data',function(done){
		var aPromise = expect(bdpMuni.getInputData().then((result) => {
			done();
		}))
		aPromise.to.eventually.be.fulfilled;
		aPromise


	});
});

