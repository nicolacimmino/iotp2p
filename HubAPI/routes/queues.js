/* queues.js is part of IoTHub API and is responsible to
 *      provide routing for API requests to the queues resource.
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

var express = require('express');
var router = express.Router();
var ObjectId = require('mongodb').ObjectID;
var accessControl = require('../accessControl.js');

/* HTTP GET /queues/:username?mac=macValue
 * Param username: the username of the owner of the queue.
 * Query param mac: a valid MAC generated with an adminKey
 * Returns: all queues for the specified user.
 * Error: 401 if the macValue doesn't authorize the operation.
 */
router.get('/:username', function(req, res) {
  
  var db = req.db;
  var username = req.params.username;
  var mac =  req.query.mac;
  
  accessControl.authorizeAdmin(username, mac, 
      function onAllowed() {
      
        // TODO fetch from redis if availalble.
        
        db.collection('queues').find({ username: username },{}).sort({ name:-1}, function(e,docs){
          try {
            res.json( docs );
          } catch (e) {
            res.send(401);
          }
        })},
      function onDenied() {
        res.send(401);
      });
});

/* HTTP GET /queues/:username/:id?mac=macValue
 * Param username: the username of the user.
 * Param id: the id of the queue.
 * Query param mac: a valid MASC generated with a readKey
 * Returns: the tansactions inside the specified queue.
 * Error: 401 if the readKey doesn't authorize the operation.
 */
router.get('/:username/:id', function(req, res) {

  var db = req.db;
  var username = req.params.username;
  var mac =  req.query.mac;
  var id =  req.params.id;
  
  accessControl.authorizeRead(username, mac, 
      function onAllowed() {
        db.collection('transactions').find({ username: username , queue_id:new ObjectId(id) },{}, function(e,docs){
          try {
            res.json( docs );
          } catch (e) {
            res.send(401);
          }
        })},
      function onDenied() {
        res.send(401);
      });
});

/* HTTP POST /queues/:username/:queueId?mac=mac
 * Param username: the username of the user owning the queue.
 * Param id: the id of the queue.
 * Query param mac: a valid MAC generated with a createKey
 * POST data: a json document describing the transaction
 * Returns: 200 on success.
 * Error: 401 if the MAC doesn't authorize the operation.
 */
router.post('/:username/:queueId', function(req, res) {

  var db = req.db;
  var username = req.params.username;
  var queueId = req.params.queueId;
  var mac =  req.query.mac;
  
  accessControl.authorizeCreate(username, mac, 
      function onAllowed() {
        try {
          // We take the documents as it came in the body as base for the trasaction
          transaction = req.body;
          
          // TODO!
          // Sanitize (e.g. if some fields are needed from the system prevent them to leak in (blacklisting)
          // or if a more structured document is desired allow only certain values in the doc (whitelist)).
          // One more option is to make the whole document a value inside a document that represents the transaction
          // (e.g. id, username, queue and document) so application is isolated from the values.
          transaction.username = username;
          transaction.queueId = queueId;
          
          db.collection('transactions').insert(transaction,{}, function(e,docs){
            res.send(200);
          });
        } catch (Exception) {
             res.send(401);
        }            
      },
      function onDenied() {
        res.send(401);
      });
});

module.exports = router;
