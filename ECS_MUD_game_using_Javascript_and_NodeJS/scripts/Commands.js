/**
 * scripts/Commands.js
 * 
 * This file provides the main game logic;
 *
 * @author Jonathon Hare (jsh2@ecs.soton.ac.uk)
 * @author Richa Ranjan (rr2n17@ecs.soton.ac.uk)
 */
var db = require('../models');
var controller = require('./Controller');
var predicates = require('./Predicates');
var strings = require('./Strings');
var CommandHandler = require('./CommandHandler');
var PropertyHandler = require('./PropertyHandler');
var bfs = require('async-bfs');


/**
 * The commands object is like a map of control strings (the commands detailed 
 * in the ECS-MUD guide) to command handlers (objects extending from the 
 * CommandHandler object) which perform the actions of the required command.
 * 
 * The controller (see Controller.js) parses the statements entered by the user,
 * and passes the information to the matching property in the commands object.
 */
var commands = {
	//handle user creation
	create: CommandHandler.extend({
		nargs: 2,
		preLogin: true,
		postLogin: false,
		validate: function (conn, argsArr, cb) {
			if (!predicates.isUsernameValid(argsArr[0])) {
				controller.sendMessage(conn, strings.badUsername);
				return;
			}

			if (!predicates.isPasswordValid(argsArr[1])) {
				controller.sendMessage(conn, strings.badPassword);
				return;
			}

			controller.loadMUDObject(conn, { name: argsArr[0], type: 'PLAYER' }, function (player) {
				if (!player) {
					cb(conn, argsArr);
				} else {
					controller.sendMessage(conn, strings.usernameInUse);
				}
			});
		},
		perform: function (conn, argsArr) {
			//create a new player
			controller.createMUDObject(conn,
				{
					name: argsArr[0],
					password: argsArr[1],
					type: 'PLAYER',
					locationId: controller.defaultRoom.id,
					targetId: controller.defaultRoom.id
				}, function (player) {
					if (player) {
						player.setOwner(player).then(function () {
							//resync with db to ensure all fields set correctly
							player.reload().then(function () {
								controller.activatePlayer(conn, player);
								controller.broadcastExcept(conn, strings.hasConnected, player);

								controller.clearScreen(conn);
								commands.look.perform(conn, []);
							});
						});
					}
				});
		}
	}),
	//handle connection of an existing user
	connect: CommandHandler.extend({
		nargs: 2,
		preLogin: true,
		postLogin: false,
		validate: function (conn, argsArr, cb) {
			controller.loadMUDObject(conn, { name: argsArr[0], type: 'PLAYER' }, function (player) {
				if (!player) {
					controller.sendMessage(conn, strings.playerNotFound);
					return;
				}

				if (player.password !== argsArr[1]) {
					controller.sendMessage(conn, strings.incorrectPassword);
					return;
				}

				cb(conn, argsArr);
			});
		},
		perform: function (conn, argsArr) {
			//load player if possible:
			controller.loadMUDObject(conn, { name: argsArr[0], password: argsArr[1], type: 'PLAYER' }, function (player) {
				if (player) {
					controller.applyToActivePlayers(function (apconn, ap) {
						if (ap.name === argsArr[0]) {
							//player is already connected... kick them off then rejoin them
							controller.deactivatePlayer(apconn);
							return false;
						}
					});

					controller.activatePlayer(conn, player);
					controller.broadcastExcept(conn, strings.hasConnected, player);

					controller.clearScreen(conn);
					commands.look.perform(conn, []);
				}
			});
		}
	}),
	//Disconnect the player
	QUIT: CommandHandler.extend({
		preLogin: true,
		perform: function (conn, argsArr) {
			conn.terminate();
		}
	}),
	//List active players
	WHO: CommandHandler.extend({
		preLogin: true,
		perform: function (conn, argsArr) {
			controller.applyToActivePlayers(function (otherconn, other) {
				if (otherconn !== conn) {
					controller.sendMessage(conn, other.name);
				}
			});
		}
	}),
	//Speak to other players
	say: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {
			var message = argsArr.length === 0 ? "" : argsArr[0];
			var player = controller.findActivePlayerByConnection(conn);

			controller.sendMessage(conn, strings.youSay, { message: message });
			controller.sendMessageRoomExcept(conn, strings.says, { name: player.name, message: message });
		}
	}),
	
	//Whisper to other players
	whisper: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			var message = argsArr.length === 0 ? "" : argsArr[0];
			var player = controller.findActivePlayerByConnection(conn);
			var player2_name = argsArr.length === 0 ? "" : argsArr[0].split("=")[0];
			message = argsArr[0].split("=")[1];
			var player2 = controller.findActivePlayerByName(player2_name);
			//	console.log("Player 2 "+player2_name+ " is "+player2);
			if (player2 == undefined) {
				controller.sendMessage(conn, strings.notConnected, { name: player2_name });
				return;
			}
			controller.sendMessage(conn, strings.youWhisper, { name: player2.name, message: message });
			//controller.sendMessageRoomExcept(conn, strings.toWhisper, {name: player.name, message: message});
			var conn2 = controller.findActiveConnectionByPlayer(player2);

			if (player2.locationId === player.locationId && player2 !== player) {
				controller.sendMessage(conn2, strings.toWhisper, { name: player.name, message: message });
			}
			else
			{
				controller.sendMessage(conn, strings.notInRoom);
			}

			var num = Math.floor((Math.random() * 10) + 1);
			//console.log("Random number generated is: ");
			if (num !== 5) {
				controller.applyToActivePlayers(function (otherconn, other) {
					if (other.locationId === player.locationId && player !== other && player2 !== other) {
						controller.sendMessage(otherconn, strings.whisper, { fromName: player.name, toName: player2.name });
					}
				});
			}
			else {
				controller.applyToActivePlayers(function (otherconn, other) {
					if (other.locationId === player.locationId && player !== other && player2 !== other) {
						controller.sendMessage(otherconn, strings.overheard, { fromName: player.name, toName: player2.name, message: message });
					}
				});
			}

		}
	}),

	//implementing inventory
	inventory: CommandHandler.extend({
		nargs: 0,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);

			//console.log("Player is: " + player.name);
			if (player) {
				commands.look.lookContents(conn, player, strings.youAreCarrying, strings.carryingNothing);
			}

		}
	}),

	//implementing @open
	"@open": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			controller.loadMUDObject(conn, { id: player.locationId }, function (currentRoom) {
				if (currentRoom.ownerId != player.id)
					controller.sendMessage(conn, strings.permissionDenied);
				else {
					if (argsArr.length === 0) {
						controller.sendMessage(conn, strings.invalidName);
					}
					else {
						controller.loadMUDObjects(conn, { name: argsArr[0] }, function (objs) {
							if (objs.length > 0)
								controller.sendMessage(conn, strings.invalidName);

							else {
								controller.createMUDObject(conn, { name: argsArr[0], type: 'EXIT', locationId: player.locationId }, function (exitname) {
									if (!exitname) {
										controller.sendMessage(conn, strings.invalidName);
									}
									else {

										controller.sendMessage(conn, strings.opened);
									}

								});

							}

						});
					}
				}
			});
		}
	}),



	//find command start
	"@find": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {
			var name = argsArr.length === 0 ? "" : argsArr[0];
			var player = controller.findActivePlayerByConnection(conn);
			var escName = '%' + name.toLowerCase() + '%';
			var escType = '*';
			try {
				if (escType) {
					controller.loadMUDObjects(conn,
						db.Sequelize.and(
							["lower(name) LIKE ?", [escName]],
							{'ownerId':player.id}

						), function (objs) 
						{
							if (objs.length === 0) {
								controller.sendMessage(conn, strings.notFound);
								return;
							}
							for (i = 0; i < objs.length; i++) {
								controller.sendMessage(conn, strings.roomNameOwner, { name: objs[i].name, id: objs[i].id });
							}
						}
					);
				}
			}
			catch (err) { console.log(err); }
		}
	}),


	//implementing @create
	"@create": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {

			if (predicates.isNameValid(argsArr[0].trim()) === false) {
				controller.sendMessage(conn, strings.invalidName);
			}
			else {
				var player = controller.findActivePlayerByConnection(conn);
				controller.createMUDObject(conn, { name: argsArr[0], type: 'THING', targetId: player.targetId }, function (thing) {
					if (thing) {
						thing.setOwner(player.id);
						thing.setLocation(player.id);
						controller.sendMessage(conn, strings.created);
					}
				}
				);

			}
		}
	}),


	//implementing @dig
	"@dig": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			controller.createMUDObject(conn, { name: argsArr[0], type: 'ROOM' }, function (room) {
				if (!room) {
					controller.sendMessage(conn, strings.invalidName);
				}
				else {
					room.ownerId = player.id;
					room.save();
					controller.sendMessage(conn, strings.roomCreated, { name: room.name, id: room.id });
				}
			}
			);
		}
	}),

	//implementing @password
	"@password": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			var pswd_old = argsArr.length === 0 ? "" : argsArr[0].split("=")[0];
			var pswd_new = argsArr[0].split("=")[1];
			if (pswd_old === player.password) {
				player.password = pswd_new;
				player.save();
				controller.sendMessage(conn, strings.changePasswordSuccess);
			}

			else {
				controller.sendMessage(conn, strings.changePasswordFail);
			}

		}
	}),


	//page a player
	page: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {
			//var message = argsArr.length === 0 ? "" : argsArr[0];
			var player1 = controller.findActivePlayerByConnection(conn);
			var player2_name = argsArr.length === 0 ? "" : argsArr[0];
			//var player2 = controller.findActivePlayerByName(player2_name);
			controller.loadMUDObject(conn, { name: player2_name, type: 'PLAYER' }, function (player2) {
				if (!player2) {
					controller.sendMessage(conn, strings.isNotAvailable);
					return;
				}
				else {
					controller.sendMessage(conn, strings.pageOK);
					//var player1_name = player1.name;
					var loc = player1.locationId;
					var conn2 = controller.findActiveConnectionByPlayer(player2);
					controller.loadMUDObject(conn, { id: loc }, function (my_loc) {

						controller.sendMessage(conn2, strings.page, { name: player1.name, location: my_loc.name });
					});
				}

			});
		}
	}),
	//move the player somewhere
	go: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr, errMsg) {
			var player = controller.findActivePlayerByConnection(conn);
			var exitName = argsArr[0];

			if (exitName === 'home') {
				player.getTarget().then(function (loc) {
					controller.applyToActivePlayers(function (otherconn, other) {
						if (other.locationId === loc.id && player !== other) {
							controller.sendMessage(otherconn, strings.goesHome, { name: player.name });
						}
					});

					player.getContents().then(function (contents) {
						var fcn = function () {
							if (contents && contents.length > 0) {
								var e = contents.shift();
								e.locationId = e.targetId;
								e.save().then(fcn);
							} else {
								for (var i = 0; i < 3; i++)
									controller.sendMessage(conn, strings.noPlaceLikeHome);

								player.setLocation(loc).then(function () {
									controller.sendMessage(conn, strings.goneHome);
									commands.look.lookRoom(conn, loc);
								});
							}
						}
						fcn();
					});
				});
			} else {
				controller.findPotentialMUDObject(conn, exitName, function (exit) {
					//found a matching exit... can we use it?
					predicates.canDoIt(controller, player, exit, function (canDoIt) {
						if (canDoIt && exit.targetId) {
							exit.getTarget().then(function (loc) {
								if (loc.id !== player.locationId) {
									//only inform everyone else if its a different room
									controller.applyToActivePlayers(function (otherconn, other) {
										if (other.locationId === player.locationId && player !== other) {
											controller.sendMessage(otherconn, strings.leaves, { name: player.name });
										}
										if (other.locationId === loc.id && player !== other) {
											controller.sendMessage(otherconn, strings.enters, { name: player.name });
										}
									});

									player.setLocation(loc).then(function () {
										commands.look.lookRoom(conn, loc);
									});
								} else {
									commands.look.lookRoom(conn, loc);
								}
							});
						}
					}, strings.noGo);
				}, false, false, 'EXIT', strings.ambigGo, errMsg ? errMsg : strings.noGo);
			}
		}
	}),
	//look at something
	look: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length <= 1)
				cb(conn, argsArr);
			else
				controller.sendMessage(conn, strings.unknownCommand);
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);

			if (argsArr.length === 0 || argsArr[0].length === 0) {
				player.getLocation().then(function (room) {
					commands.look.look(conn, room);
				});
			} else {
				controller.findPotentialMUDObject(conn, argsArr[0], function (obj) {
					commands.look.look(conn, obj);
				}, true, true, undefined, undefined, undefined, true);
			}
		},
		look: function (conn, obj) {
			switch (obj.type) {
				case 'ROOM':
					commands.look.lookRoom(conn, obj);
					break;
				case 'PLAYER':
					commands.look.lookSimple(conn, obj);
					commands.look.lookContents(conn, obj, strings.carrying);
					break;
				default:
					commands.look.lookSimple(conn, obj);
			}
		},
		lookRoom: function (conn, room) {
			var player = controller.findActivePlayerByConnection(conn);

			if (predicates.isLinkable(room, player)) {
				controller.sendMessage(conn, strings.roomNameOwner, room);
			} else {
				controller.sendMessage(conn, strings.roomName, room);
			}
			if (room.description) controller.sendMessage(conn, room.description);

			predicates.canDoIt(controller, player, room, function () {
				commands.look.lookContents(conn, room, strings.contents);
			});
		},
		lookSimple: function (conn, obj) {
			controller.sendMessage(conn, obj.description ? obj.description : strings.nothingSpecial);
		},
		lookContents: function (conn, obj, name, fail) {

			obj.getContents().then(function (contents) {

				if (contents) {
					var player = controller.findActivePlayerByConnection(conn);

					contents = contents.filter(function (o) {
						return predicates.isLookable(player, o);
					});

					if (contents.length > 0) {

						controller.sendMessage(conn, name);
						for (var i = 0; i < contents.length; i++) {
							controller.sendMessage(conn, contents[i].name);
						}
					} else {
						if (fail)
							controller.sendMessage(conn, fail);
					}
				}

			});
		}
	}),


	//implementing set
	"@set": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length <= 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {

			if (argsArr.length === 0) {
				controller.sendMessage(conn, strings.setUnknown);
				return;
			}


			var player = controller.findActivePlayerByConnection(conn);
			var objname = argsArr.length === 0 ? "" : argsArr[0].split("=")[0];
			var arg = argsArr[0].split("=")[1];
			var flagName = (arg.indexOf("!") === -1) ? arg : (arg.substr(1));

			if (objname === '')
				controller.sendMessage(conn, strings.setUnknown);
			else {
				controller.loadMUDObjects(conn, { name: objname }, function (things) {
					if (things.length === 0)
						controller.sendMessage(conn, strings.dontSeeThat);
					else if (things.length > 1) {
						controller.sendMessage(conn, strings.ambigSet);
					}
					else {
						reset = false;
						if (arg.indexOf('!') > -1)
							reset = true;

						if (things[0].ownerId != player.id) {
							controller.sendMessage(conn, strings.permissionDenied);
						}
						else {
							var flagbit = db.MUDObject.FLAGS[flagName];

							if (reset) {

								things[0].resetFlag(flagbit);
								controller.sendMessage(conn, strings.reset, { property: flagName });
							}

							else {

								things[0].setFlag(flagbit);
								controller.sendMessage(conn, strings.set, { property: flagName });
							}

						}

					}
				}
				);
			}
		}
	}),

	//link something
	"@link": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1)
				cb(conn, argsArr);
			else
				controller.sendMessage(conn, strings.unknownCommand);
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			var left = argsArr.length === 0 ? "" : argsArr[0].split("=")[0];
			var right = argsArr[0].split("=")[1];
			if (left === '' || right === '')
			{
				controller.sendMessage(strings.unknownCommand);
				return;
			}
			
			else {
				controller.findPotentialMUDObject(conn, left, function (objs) 
				{
						switch (objs.type) {
							case 'EXIT': if (objs.locationId !== player.locationId)
											controller.sendMessage(strings.permissionDenied);
										else
											commands.linkExit(conn, player, objs, right);
										break;

							case 'THING':	commands.linkObj(conn, player, objs, right);
											break;

							case 'ROOM':	commands.linkObj(conn, player, objs, right);
											break;

							default:	if (left === 'me' || left === 'Me' || left === 'ME') 
												commands.linkObj(conn, player, player, right);
										 break;

						}
				},true,true,undefined,strings.ambigSet,strings.unknownCommand);
			}
		}
	}),


	//Function for exit
	linkExit: function (conn, player, obj, roomNum) {
		if (obj.targetId !== null)
			controller.sendMessage(conn, strings.permissionDenied);
		else {
			switch (roomNum)
			{
				case 'here':
				case 'HERE': player.getLocation().then(function (room) 
							{
								if (room.getFlag('link_ok') !== 1) 
								{
									if (room.ownerId === player.id)
									 {
										obj.targetId = player.locationId;
										obj.setOwner(player.id);
										obj.save();
										controller.sendMessage(conn, strings.linked);
									}
									else
										controller.sendMessage(conn, strings.permissionDenied);
								}
								else 
								{
									obj.targetId = player.locationId;
									obj.setOwner(player.id);
									obj.save();
									controller.sendMessage(conn, strings.linked);
								}
							});
							break;

				case 'home':
				case 'HOME': controller.loadMUDObject(conn, { id: player.targetId }, function (room) 
							{
								if (room.getFlag('link_ok') !== 1) 
								{
									if (room.ownerId === player.id) 
									{
										obj.targetId = player.targetId;
										obj.setOwner(player.id);
										obj.save();
										controller.sendMessage(conn, strings.homeSet);
									}
									else
										controller.sendMessage(conn, strings.permissionDenied);
								}
								else 
								{
									obj.targetId = player.targetId;
									obj.setOwner(player.id);
									obj.save();
									controller.sendMessage(conn, strings.homeSet);
								}
							});
							break;

				default: controller.loadMUDObject(conn, { id: roomNum }, function (room) 
						{
							if (!room)
								controller.sendMessage(conn, strings.notARoom);
							else if (room.getFlag('link_ok') !== 1)
							 {
								if (room.ownerId === player.id) 
								{
									obj.targetId = room.id;
									obj.setOwner(player.id);
									obj.save();
									controller.sendMessage(conn, strings.linked);
								}
								else
									controller.sendMessage(conn, strings.permissionDenied);
							}
							else 
							{
								obj.targetId = room.id;
								obj.setOwner(player.id);
								obj.save();
								controller.sendMessage(conn, strings.linked);
							}
						});

			}
		}
	},


	//linking object
	linkObj: function (conn, player, obj, roomNum) {
		//console.log("LHS is: " + obj.name + "and RHS is: " + roomNum);
		if (!predicates.isLinkable(obj, player)) {
			controller.sendMessage(conn, strings.permissionDenied);
			return;
		}


		switch (roomNum)
		 {
			case 'here':
			case 'HERE': player.getLocation().then(function (room) 
						{
							if (room.getFlag('link_ok') !== 1)
							 {
								if (room.ownerId === player.id) 
								{
									obj.targetId = player.locationId;
									obj.save();
									controller.sendMessage(conn, strings.linked);
								}
								else
									controller.sendMessage(conn, strings.permissionDenied);
							}
							else 
							{
								obj.targetId = player.locationId;
								obj.save();
								controller.sendMessage(conn, strings.linked);
							}
						});
						break;

			case 'home':
			case 'HOME': controller.loadMUDObject(conn, { id: player.targetId }, function (room) 
						{
							if (room.getFlag('link_ok') !== 1) 
							{
								if (room.ownerId === player.id)
								 {
									obj.targetId = player.targetId;
									obj.save();

									if (obj.id === player.locationId)
										controller.sendMessage(conn, strings.set, { property: "Home" });

									else
										controller.sendMessage(conn, strings.homeSet);
								}
								else
									controller.sendMessage(conn, strings.permissionDenied);
							}
							else 
							{
								obj.targetId = player.targetId;
								obj.save();
								if (obj.id === player.locationId)
										controller.sendMessage(conn, strings.set, { property: "Home" });
								else
										controller.sendMessage(conn, strings.homeSet);
							}
						});
						break;

			default: controller.loadMUDObject(conn, { id: roomNum }, function (room)
					 {
						//console.log("Room name is: " + room.name);
						if (!room)
							controller.sendMessage(conn, strings.notARoom);
						else if (room.getFlag('link_ok') !== 1) 
						{
							if (room.ownerId === player.id)
							 {
								obj.targetId = room.id;
								obj.save();
								controller.sendMessage(conn, strings.linked);
							}
							else
								controller.sendMessage(conn, strings.permissionDenied);
						}
						else 
						{
							obj.targetId = room.id;
							obj.save();
							controller.sendMessage(conn, strings.linked);
						}
				});

		}
	},

	//implementing unlink
	"@unlink": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1)
				cb(conn, argsArr);
			else
				controller.sendMessage(conn, strings.unknownCommand);
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			controller.loadMUDObjects(conn, { name: argsArr[0], type: 'EXIT' }, function (exitName) {
				if (exitName.length === 0)
					controller.sendMessage(conn, strings.unlinkUnknown);
				else if (exitName.length > 1)
					controller.sendMessage(conn, strings.ambigSet);
				else {
					if (exitName[0].ownerId === player.id) {
						exitName[0].targetId = null;
						exitName[0].save();
						controller.sendMessage(conn, strings.unlinked);
					}
					else
						controller.sendMessage(conn, strings.permissionDenied);
				}
			});
		}
	}),

	//implementing examine
	examine: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {

			var player = controller.findActivePlayerByConnection(conn);
			var objname = argsArr[0];
			if (objname == null)
				controller.sendMessage(conn, strings.examineUnknown);
			else {

				controller.findPotentialMUDObject(conn, objname, function (objs) {
					console.log("Object name is: "+objs);
					switch (objs.type) {
						case 'THING':
						case 'EXIT': if ((objs.ownerId === player.id) && ((objs.locationId === player.locationId) || (objs.locationId === player.id)))
										commands.examine.examineObj(conn, player, objs);
									else
										controller.sendMessage(conn, strings.permissionDenied);
									break;


						case 'PLAYER': if (objs.id === player.id) 
										{
											commands.examine.examineObj(conn, player, objs);
											objs.getContents().then(function (contents) 
											{
												if (contents.length > 0)
												{
													controller.sendMessage(conn, strings.contents);
													for (i = 0; i < contents.length; i++) 
													{
														controller.sendMessage(conn, strings.examineContentsName, { type: contents[i].type, name: contents[i].name });
													}
												}
											});
										}
										else
											controller.sendMessage(conn, strings.permissionDenied);
										break;

						case 'ROOM': if (objs.id === player.locationId)
									 {
										commands.examine.examineObj(conn, player, objs);
										objs.getContents().then(function (contents) 
										{
											if (contents.length > 0) 
											{
												controller.sendMessage(conn, strings.contents);
												for (i = 0; i < contents.length; i++) 
												{
													controller.sendMessage(conn, strings.examineContentsName, { type: contents[i].type, name: contents[i].name });
												}
											}
										});
									}
									else
										controller.sendMessage(conn, strings.permissionDenied);
									break;
						default: controller.sendMessage(conn, strings.examineUnknown);
					}


				}, true, true, undefined, strings.ambigSet, strings.examineUnknown);
			}
		},
		examineObj: function (conn, player, obj) {

			controller.sendMessage(conn, strings.examine,
				{
					name: obj.name,
					id: obj.id,
					description: obj.description,
					failureMessage: obj.failureMessage,
					successMessage: obj.successMessage,
					othersFailureMessage: obj.othersFailureMessage,
					othersSuccessMessage: obj.othersSuccessMessage,
					type: obj.type,
					flags: obj.flags,
					password: obj.password,
					targetId: obj.targetId,
					locationId: obj.locationId,
					ownerId: obj.ownerId,
					keyId: obj.keyId
				});


		}

	}),

	//implementing @lock
	"@lock": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			try {
				var player = controller.findActivePlayerByConnection(conn);

				if (argsArr[0].indexOf("=") === -1) {
					controller.sendMessage(conn, strings.unknownCommand);
				}
				else {
					var objname = argsArr[0].split("=")[0];
					var keyname = argsArr[0].split("=")[1];
					if (objname === '')
						controller.sendMessage(conn, strings.lockUnknown);
					else if (keyname === '')
						controller.sendMessage(conn, strings.keyUnknown);
					else {
						controller.findPotentialMUDObject(conn, objname, function (objs) {
							if (objs.ownerId !== player.id)
								controller.sendMessage(conn, strings.permissionDenied);

							else if ((objs.locationId === player.id) || (objs.locationId === player.locationId)) {
								if (objs.hasAntiLock()) {
									controller.findPotentialMUDObject(conn, keyname, function (keys) {
										if ((keys.locationId !== player.id) && (keys.id !== player.id) && (keys.locationId === player.locationId)) {
											objs.setKey(keys);
											controller.sendMessage(conn, strings.locked);
										}
										else
											controller.sendMessage(conn, strings.permissionDenied);

									}, true, true, undefined, strings.ambigSet, strings.dontSeeThat);
								}
								else {
									controller.findPotentialMUDObject(conn, keyname, function (keys) {
										if ((keys.locationId === player.id) || (keys.locationId === player.locationId)) {
											objs.setKey(keys);
											controller.sendMessage(conn, strings.locked);
										}
										else
											controller.sendMessage(conn, strings.permissionDenied);

									}, true, true, undefined, strings.ambigSet, strings.dontSeeThat);
								}

							}
						}, true, true, undefined, strings.ambigSet, strings.dontSeeThat);
					}

				}
			} catch (err) { console.log(err); }
		}
	}),


	//implementing unlock
	"@unlock": CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			if (argsArr.length === 1) {
				cb(conn, argsArr);
			} else {
				controller.sendMessage(conn, strings.unknownCommand);
			}
		},
		perform: function (conn, argsArr) {
			try {
				var player = controller.findActivePlayerByConnection(conn);
				var objname = argsArr[0];
				controller.findPotentialMUDObject(conn, objname, function (objs) {
					if (objs.ownerId !== player.id)
						controller.sendMessage(conn, strings.permissionDenied);

					else if ((objs.locationId === player.id) || (objs.locationId === player.locationId)) {

						objs.setKey(null);
						controller.sendMessage(conn, strings.unlocked);
					}

					else
						controller.sendMessage(conn, strings.dontSeeThat);

				}, true, true, undefined, strings.ambigSet, strings.unlockUnknown);

			} catch (err) { console.log(err); }
		}
	}),


	//implementing take command
	take: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {

			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {

			var player = controller.findActivePlayerByConnection(conn);
			var objname = argsArr[0];
			controller.findPotentialMUDObject(conn, objname, function (obj) {
				//console.log("No. of objects=" + obj.length);

				if (obj.locationId === player.id)
					controller.sendMessage(conn, strings.alreadyHaveThat);
				else if (obj.locationId != player.locationId)
					controller.sendMessage(conn, strings.cantTakeThat);

				else {
					try {
						predicates.canDoIt(controller, player, obj, function (doit) {
							if (doit) {
								obj.setLocation(player.id);
								obj.save();
								controller.sendMessage(conn, strings.taken);
							}
						}, strings.cantTakeThat);

					} catch (err) { console.log(err); }


				}

			}, true, true, 'THING', strings.ambigSet, strings.takeUnknown);

		}
	}),

	//drop command
	drop: CommandHandler.extend({
		nargs: 1,
		validate: function (conn, argsArr, cb) {
			cb(conn, argsArr);
		},
		perform: function (conn, argsArr) {
			var player = controller.findActivePlayerByConnection(conn);
			controller.findPotentialMUDObject(conn, argsArr[0], function (thing) {
				if (thing.locationId === player.id) {
					controller.loadMUDObject(conn, { type: 'ROOM', id: player.locationId }, function (room) {
						if (room.getFlag('temple') === 4) {
							if (thing.targetId !== null)
								thing.locationId = thing.targetId;
							else
								thing.locationId = room.id;
							thing.save();
							controller.sendMessage(conn, strings.dropped);
						}
						else {
							if (room.targetId !== null) {
								thing.locationId = room.targetId;
								thing.save();
								controller.sendMessage(conn, strings.dropped);
							}
							else {
								thing.locationId = room.id;
								thing.save();
								controller.sendMessage(conn, strings.dropped);
							}
						}

					});
				}
				else
					controller.sendMessage(conn, strings.dontHave);
			}, true, true, 'THING', strings.ambigSet, strings.dontHave);
		}
	}),


	//set the description of something
	"@describe": PropertyHandler.extend({
		prop: 'description'
	}),

	//change the name of something
	"@name": PropertyHandler.extend({
		prop: 'name'
	}),

	//implementing success
	"@success": PropertyHandler.extend({
		prop: 'successMessage'
	}),

	//implementing others success
	"@osuccess": PropertyHandler.extend({
		prop: 'othersSuccessMessage'
	}),

	//implementing failure
	"@failure": PropertyHandler.extend({
		prop: 'failureMessage'
	}),

	//implementing others failure
	"@ofailure": PropertyHandler.extend({
		prop: 'othersFailureMessage'
	}),

};

//command aliases
commands.goto = commands.go;
commands.move = commands.go;
commands.cr = commands.create;
commands.co = commands.connect;
commands.read = commands.look;
commands.get = commands.take;
commands.throw = commands.drop;


//The commands object is exported publicly by the module
module.exports = commands;
