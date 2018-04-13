/**
 * models/index.js
 * 
 * Entry point for sequelize database definition
 *
 * @author Jonathon Hare (jsh2@ecs.soton.ac.uk)
 */
if (!global.hasOwnProperty('db')) {
  var Sequelize = require('sequelize');
  var sequelize = null;

  var dbUrl = process.env.DATABASE_URL;

  //if the heroku database is set, it will be used  
  if (dbUrl) {
    //parse the url
    var match = dbUrl.match(/postgres:\/\/([^:]+):([^@]*)@([^:]+):(\d+)\/(.+)/);

    // construct the sequelize object
    sequelize = new Sequelize(match[5], match[1], match[2], {
      dialect:  'postgres',
      protocol: 'postgres',
      port:     match[4],
      host:     match[3],
      logging:  console.log
    });
  } else {
    //otherwise we'll just use SQLite (which doesn't require any setup :))
    sequelize = new Sequelize('database', 'username', 'password', {
      dialect: 'sqlite',
      storage: './dev-database.sqlite'
    });
  }
  
  //define the database
  global.db = {
    Sequelize:  Sequelize,
    sequelize:  sequelize,
    MUDObject:  sequelize.import(__dirname + '/MUDObject')
  };

  //add relations/assocations by calling the `associate` method defined in the model
  Object.keys(global.db).forEach(function(modelName) {
    if ('associate' in global.db[modelName]) {
      global.db[modelName].associate(global.db);
    }
  });
}

module.exports = global.db;

var pg = require('pg');
var express = require('express');
var app = express();

app.get('/db', function (request, response) {
  pg.connect(process.env.DATABASE_URL, function(err, client, done) {
    client.query('SELECT * FROM test_table', function(err, result) {
      done();
      if (err)
       { console.error(err); response.send("Error " + err); }
      else
       { response.render('pages/db', {results: result.rows} ); }
    });
  });
});
