/* accessControl.js is part of IotHub API and is responsible to
 ~      provide access control for API requests.
 *
 *   Copyright (C) 2014 Nicola Cimmino
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
                    'auth_token': buf.toString('hex') 
                    },
                    function(err, doc) {
                      if(err) {
                        onDenied();
                      } else {
                        onAllowed({auth_token: buf.toString('hex')});
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

// NOTE: The methods below allow to authorize each of the four CRUD operation separately. We don't
//  have yet ACLs in place so they all have the same implementation at the moment. In other words
//  a valid token allows all CRUD operations. Defining the functions now though allows to freeze
//  the interface so we don't have to change the rest of the code when ACLs are in place.

// TODO add method to authorize admin request

// Checks if the supplied token allows create operations on a resource owned by username.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeCreate = function (username, auth_token, onAllowed, onDenied) {

    // TODO
    // change to take message data, HMAC, username as params
    // Try to finnd adminKey in redis
    // if not found search from db
    // generate HMAC
    // comapare safely HMAC
       
    dbMongo.collection('auth_tokens').find({auth_token:auth_token, username:username} , function(e, docs) {
      if(docs.length === 1) {
        onAllowed();
      } else {
        onDenied();
      }
    }); 
};

// Checks if the supplied token allows read operations on a resource owned by username.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeRead = function (username, auth_token, onAllowed, onDenied) {
    dbMongo.collection('auth_tokens').find({auth_token:auth_token, username:username} , function(e, docs) {
      if(docs.length === 1) {
        onAllowed();
      } else {
        onDenied();
      }
    }); 
};

// Checks if the supplied token allows update operations on a resource owned by username.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeUpdate = function (username, auth_token, onAllowed, onDenied) {
    dbMongo.collection('auth_tokens').find({auth_token:auth_token, username:username} , function(e, docs) {
      if(docs.length === 1) {
        onAllowed();
      } else {
        onDenied();
      }
    }); 
};

// Checks if the supplied token allows delete operations on a resource owned by username.
// Takes two callback function that are called in case of operation permitted or denied respectively.
module.exports.authorizeDelete = function (username, auth_token, onAllowed, onDenied) {
    dbMongo.collection('auth_tokens').find({auth_token:auth_token, username:username} , function(e, docs) {
      if(docs.length === 1) {
        onAllowed();
      } else {
        onDenied();
      }
    }); 
};
