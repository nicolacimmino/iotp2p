/* app.js is part of IoTHub API and bootstraps the application.
 *
 *   Copyright (C) 2015 Nicola Cimmino
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program.  If not, see http://www.gnu.org/licenses/.
 *
 */
 
// Mongo database connection
// We make use of mongojs as it provides usability improvements over mongodb.
// See https://www.npmjs.org/package/mongojs for info and documentation.
var mongo = require('mongodb');
var mongojs = require('mongojs');
var db = mongojs('IoTHub');

// We use path to build some static referneces to local folders below.
var path = require('path');

// We use express as web server framework.
// See https://www.npmjs.org/package/express for info and documentation.
var express = require('express');
var app = express();

// Morgan is middleware that pretty prints a log of each HTTP request along with response status code.
// https://www.npmjs.org/package/morgan
var morgan = require('morgan');
app.use(morgan('dev'));

// Bodyparser is middleware that takes care to parse request bodies and make them readily available in
// the request object. We make use of "JSON".json" parser  which will populate request.body if the request
// body MIME type is "application/json". We also use  ".urlencoded" which will populate request.body if
// the body MIME type is "*/x-www-form-urlencoded".  https://www.npmjs.org/package/body-parser
var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());

// cors is middleware that takes care to set the needed  response headers to implement 
// CORS (Cross Origin Resource Sharing).  We need this as our API will be served by a certain domain but
// could be invoked by applications loaded from a different domain.  https://www.npmjs.org/package/cors
var cors = require('cors')
app.use(cors());

// Since we want to share the datagbase connection instance  with all the request handlers we add this
// middleware function  that takes care to inject the db dependency into the request  so that it's passed 
// on to all following handlers.
app.use(function(req,res,next){
    req.db = db;
    next();
});

var authentication = require('./accessControl.js');
authentication.useMongo(db);

// We finally inject our modules.
// Note that in this case when invoking  app.use() we pass a partial URL as first
// parameter so we tell Express which modules  to use according to the reuested URL.
var users = require('./routes/users');
app.use('/users', users);

// As mentioned above the middleware injected  is executed in the order in which it's injected
// so this goes at the end of the chain and will  set the response code to 404 (not found) as none
// of the above modules has found something to do  with the requested URL. Note that since the
// function we inject here has 3 parameters it will  not match errors, errors will be caught by the
// next function that has 4 parameters (Express convention).
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    // We pass (err) here instead o just using next()
    // In this way we cause the error handler to be invoked.
    next(err);
});


// And last in the chain we inject the error handler.
// This has a four parameter signature. We give a generic  500 (internal server error) unless 
// a specific error  was already set.
app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
        message: err.message,
        error: {}
    });
});

app.set('port', 3000);
var server = app.listen(app.get('port'));

