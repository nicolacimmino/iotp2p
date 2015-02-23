/* accessControl.js is part of IotHub API and is responsible to
 ~      provide access control for API requests.
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

var bcrypt = require('bcrypt');
var crypto = require('crypto');
var dbMongo;
var redis;

// Allows to inject the database dependency.
module.exports.useMongo = function(database) {
  dbMongo=database;
}

// Allows to inject the redis dependency.
module.exports.useRedis = function(redisInstance) {
  redis=redisInstance;
}

// Generates an administrator key if the supplied credentials are valid.
// The function takes two callbacks that are called in case of authentication
// success and failure respectively.
module.exports.getAdminKey  = function (username, password, onAllowed, onDenied) { 

  // Check user credentials from database, create the adminKey and store it in redis,
  // with useraname_adminkey as key.
  
  dbMongo.collection('users').find({ username:username },{}, 
      function(e,docs){
        try {
          if(docs.length == 1) {
            // compareSync compare a password with an hashed and salted password.
            // We do not store passwords in clear in db, compareSync is taking care
            //  of hasing and salting.
            if(bcrypt.compareSync(password, docs[0].password)) {
              crypto.randomBytes(48, function(ex, buf) {
                dbMongo.collection('auth_tokens').insert(
                    {
                    'username':username,
                    'adminKey': buf.toString('hex') 
                    },
                    function(err, doc) {
                      if(err) {
                        onDenied();
                      } else {
                        onAllowed({adminKey: buf.toString('hex')});
                      }
                    });
                });
            } else {
              onDenied();
            }
          } else {
            onDenied();
          }
        } catch (Exception) {
          onDenied();
        }
      });
};  

// Checks if the supplied message has been signed with the createKey.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeCreate = function (username, message, hmac, onAllowed, onDenied) {
    // Find in redis if adminKey for this user is cached
    // Get adminKey from database if needed
    // verifyHMAC(...)
};

// Checks if the supplied message has been signed with the readKey.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeRead = function (username, message, hmac, onAllowed, onDenied) {
    // Find in redis if adminKey for this user is cached
    // Get adminKey from database if needed
    // verifyHMAC(...)
};

// Checks if the supplied message has been signed with the updateKey.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeUpdate = function (username, message, hmac, onAllowed, onDenied) {
    // Find in redis if adminKey for this user is cached
    // Get adminKey from database if needed
    // verifyHMAC(...)
};

// Checks if the supplied message has been signed with the deleteKey.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeDelete = function (username, message, hmac, onAllowed, onDenied) {
    // Find in redis if adminKey for this user is cached
    // Get adminKey from database if needed
    // verifyHMAC(...)
};

// Checks if the supplied message has been signed with the adminKey.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeAdmin = function (username, message, hmac, onAllowed, onDenied) {
    // Find in redis if adminKey for this user is cached
    // Get adminKey from database if needed
    // verifyHMAC(...)
};

function verifyHMAC(message, key, rolling_code, hmac)
{
  // Generate HMAC and compare safely to supplied hmac. 
  // return true/false
};
