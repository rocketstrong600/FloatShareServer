from flask import render_template, url_for, flash, redirect, request, Response
from . import app, db_session, api_info
from .models import User, Board, Tune, Message
from .helpers import jsonRes
import json

@app.route('/')
def index():
    return jsonRes(json.dumps(api_info))

@app.route('/auth/login', methods=["GET", "POST"])
def login():
    username = request.args.get('username') or ""
    password = request.args.get('password') or ""
    app.logger.info(f"{username} Attempting Login")

    sUser: User = User.query.filter(User.username==username).first()
    if not sUser == None:
        if sUser.CheckPassword(password):
            sUser.StartSession()
            app.logger.info(f"{sUser.username} Successfull Login new session {sUser.sessionID}")
            db_session.commit()

            return jsonRes(json.dumps({**api_info, "Message": "Access Aproved", "success": 1, "sessionid": sUser.sessionID, "username": sUser.username}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/post/tune', methods=["GET", "POST"])
def postTune():
    sessionid = request.args.get('sessionid') or ""
    name = request.args.get('name') or ""
    description = request.args.get('description') or ""
    xml = request.args.get('xml') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            newTune = Tune(name=name, description=description, XML=xml, Owner=sUser.id)
            db_session.add(newTune)
            db_session.commit()
            app.logger.info(f"User {sUser.username} Posted Tune {name} With ID {newTune.id}")

            return jsonRes(json.dumps({**api_info, "Message": "Successfully Posted", "success": 1}))


    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/post/board', methods=["GET", "POST"])
def postBoard():
    sessionid = request.args.get('sessionid') or ""
    name = request.args.get('name') or ""
    description = request.args.get('description') or ""
    voltage = request.args.get('voltage') or ""
    motor = request.args.get('motor') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            newBoard = Board(name=name, description=description, voltage=int(voltage), motor=motor, odometer=0, Owner=sUser.id)
            db_session.add(newBoard)
            db_session.commit()
            app.logger.info(f"User {sUser.username} Posted Tune {name} With ID {newBoard.id}")

            return jsonRes(json.dumps({**api_info, "Message": "Successfully Posted", "success": 1}))


    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/update/tune', methods=["GET", "POST"])
def updateTune():
    sessionid = request.args.get('sessionid') or ""
    tuneID = request.args.get('id') or ""
    name = request.args.get('name') or ""
    description = request.args.get('description') or ""
    xml = request.args.get('xml') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    sTune = Tune.query.filter(Tune.id==tuneID).first()
    if sTune == None:
        return jsonRes(json.dumps({**api_info, "Message": "Tune Not Found", "success": 0}))
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            sTune.name = name
            sTune.description = description
            sTune.XML = xml
            db_session.commit()
            app.logger.info(f"User {sUser.username} updated Tune {name} With ID {sTune.id}")

            return jsonRes(json.dumps({**api_info, "Message": "Successfully Updated", "success": 1}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/get/tunes', methods=["GET", "POST"])
def getTunes():
    sessionid = request.args.get('sessionid') or ""
    tuneFilter = request.args.get('filter') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            foundTunes = []

            match tuneFilter:
                case "shared":
                    foundTunes = sUser.shared
                case "voted":
                    foundTunes = sUser.voted
                case "owned":
                    foundTunes = Tune.query.filter(Tune.Owner==sUser.id).all()
                case "id":
                    tuneID = int(request.args.get('tune') or "")
                    foundTunes = Tune.query.filter(Tune.id==tuneID).all()
                case "owner":
                    ownerID = int(request.args.get('owner') or "")
                    oUser: User = User.query.filter(User.id==ownerID).first()
                    if not oUser == None:
                        foundTunes = Tune.query.filter(Tune.Owner==oUser.id).all()
                case _:
                    foundTunes = Tune.query.filter(Tune.Public==True).all()
            
            fTunes = []
            for fTune in foundTunes:
                if fTune.Public or sUser in fTune.shared_with or fTune.Owner == sUser.id: 
                    fTunes.append({"id": fTune.id, "owner": fTune.Owner, "name": fTune.name, "description": fTune.description, "votes": fTune.votes(), "xml": fTune.XML})

            return jsonRes(json.dumps({**api_info, "Message": "Fetched Messages", "success": 1, "Tunes": fTunes}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/post/vote', methods=["GET", "POST"])
def vote():
    sessionid = request.args.get('sessionid') or ""
    tuneID = request.args.get('id') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    sTune = Tune.query.filter(Tune.id==tuneID).first()
    if sTune == None:
        return jsonRes(json.dumps({**api_info, "Message": "Tune Not Found", "success": 0}))
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            sTune.voters.append(sUser)
            db_session.commit()
            return jsonRes(json.dumps({**api_info, "Message": "Successfully Voted", "success": 1}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/post/share', methods=["GET", "POST"])
def share():
    sessionid = request.args.get('sessionid') or ""
    tuneID = request.args.get('id') or ""
    to = request.args.get('to') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    tUser: User = User.query.filter(User.username==to).first()
    sTune = Tune.query.filter(Tune.id==tuneID).first()
    if tUser == None:
        return jsonRes(json.dumps({**api_info, "Message": "User Not Found", "success": 0}))
    if sTune == None:
        return jsonRes(json.dumps({**api_info, "Message": "Tune Not Found", "success": 0}))
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            if sTune.Owner == sUser.id:
                sTune.shared_with.append(tUser)
                db_session.commit()
                return jsonRes(json.dumps({**api_info, "Message": "Successfully Shared", "success": 1}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/post/message', methods=["GET", "POST"])
def sendMessage():
    sessionid = request.args.get('sessionid') or ""
    to = request.args.get('to') or ""
    frm = request.args.get('FROM') or ""
    msg = request.args.get('MSG') or ""
    subject = request.args.get('SUB') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    tUser: User = User.query.filter(User.username==to).first()
    if tUser == None:
        return jsonRes(json.dumps({**api_info, "Message": "User Not Found", "success": 0}))
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            newMessage = Message(toUserID=tUser.id, fromUser=frm, subject=subject, message=msg)
            db_session.add(newMessage)
            db_session.commit()

            return jsonRes(json.dumps({**api_info, "Message": "Message Sent", "success": 1}))

    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))


@app.route('/get/messages', methods=["GET", "POST"])
def getMessages():
    sessionid = request.args.get('sessionid') or ""

    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            fMessages = []
            for msg in sUser.messages:
                fMessages.append({"from": msg.fromUser, "Subject": msg.subject, "Message": msg.message})

            return jsonRes(json.dumps({**api_info, "Message": "Fetched Messages", "success": 1, "Messages": fMessages}))
    
    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/auth/post/user', methods=["GET", "POST"])
def newuser():
    sessionid = request.args.get('sessionid') or ""
    username = request.args.get('username') or ""
    password = request.args.get('password') or ""
    level = request.args.get('level') or ""
    aUser: User = User.query.filter(User.username==username).first()
    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if aUser  == None and not sUser == None and not username == None or password == None:
        if sUser.CheckSession(sessionid) and sUser.level >= 9:
            app.logger.info(f"{sUser.username} Making User {username}")
            nUser = User()
            nUser.SetupUser(username, password, int(level))
            db_session.add(nUser)
            db_session.commit()
            app.logger.info(f"New User {nUser.username} SESSION {nUser.sessionID}")
            return jsonRes(json.dumps({**api_info, "Message": "User Created", "success": 1}))
    
    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/auth/update/user', methods=["GET", "POST"])
def moduser():
    sessionid = request.args.get('sessionid') or ""
    username = request.args.get('username') or ""
    password = request.args.get('password') or ""
    level = request.args.get('level') or ""

    eUser: User = User.query.filter(User.username==username).first()
    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not eUser  == None and sUser == None:
        if sUser.CheckSession(sessionid) and sUser.level >= 9:
            eUser.SetupUser(username, password, int(level))
            db_session.commit()
            app.logger.info(f"{sUser.username} Moddified User {username}")
            return jsonRes(json.dumps({**api_info, "Message": "User Modified", "success": 1}))
    
    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))

@app.route('/auth/logout', methods=["GET", "POST"])
def logout():
    sessionid = request.args.get('sessionid') or ""
    sUser: User = User.query.filter(User.sessionID==sessionid).first()
    if not sUser == None:
        if sUser.CheckSession(sessionid):
            sUser.StartSession()
            db_session.commit()
            return jsonRes(json.dumps({**api_info, "Message": "Logged Out", "success": 1}))
        
    return jsonRes(json.dumps({**api_info, "Message": "Access Denied", "success": 0}))
