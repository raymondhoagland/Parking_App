var databaseUrl = "mydb";
var collections = ["users", "reports"];
var db = require("mongojs").connect(databaseUrl, collections);

db.users.save({email: "srirangan@gmail.com", password: "iLoveMongo", sex: "male"}, function(err, saved) {
  if( err || !saved ) console.log("User not saved");
  else console.log("User saved");
});
