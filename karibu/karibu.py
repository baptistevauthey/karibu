from flask import Flask, jsonify, request
import math
from database import db_session
from models import User, Subscription, Location, Community, Vote
from sqlalchemy import desc, asc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/test_users', methods=['GET'])
def test_users():
    users = {}
    for user in User.query.all():
        user = row2dict(user)
        users[user['user_name']] = (user)
    return jsonify(users)

@app.route('/api/user/add', methods=['POST'])
def add_user():
    if not request.json:
        return jsonify({'error' : "yaahhhhh if you could send me some json that'd be great"})
    if User.query.filter(User.user_name == request.json['user_name']).count()>0:
        print User.query.filter(User.user_name == request.json['user_name']).all()
	print request.json['user_name']
        return jsonify({'error' : 'that username is already in use'})
    hashed_password = generate_password_hash(request.json['password'])
    print hashed_password
    db_session.add(User(user_name = request.json['user_name'], password = hashed_password))
    db_session.commit()
    return jsonify({'added':'true'})

@app.route('/api/user/login', methods=['POST'])
def login_user():
    if not request.json:
        return jsonify({'error' : "yo where's the json man"})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:	
	print 1
        return jsonify({'error' : "wrong username and/or password"})
    return jsonify({'logged in' : 'true'})

@app.route('/api/user/get', methods=['POST'])
def get_user():
    if not request.json:
        return jsonify({'error' : "yo where's the json man"})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:
        return jsonify({'error' : "wrong username and/or password"})
    subs = Subscription.query.filter(Subscription.user==user.id).all()
    subs_list = []
    for i in subs:
        subs_list.append(Community.query.filter(Community.id == i.community).first())
    subs_dict=({})
    for sub in subs_list:
        sub = row2dict(sub)
        subs_dict[sub['id']]=sub
    print request.json['user_name']
    print request.json['password']
    return jsonify(subs_dict)

@app.route('/api/user/subscribe', methods=['POST'])
def subscribe():
    if not request.json:
        return jsonify({'error':'JSON motherfucker, do you speak it!'})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:
        return jsonify({'error' : "wrong username and/or password"})
    if (Subscription.query.filter(Subscription.user==user.id)
        .filter(Subscription.community==request.json['community']).count()>0):
        return jsonify({'error':"You can't subscribe twice to the same place"})
    sub = Subscription(user=user.id, community=request.json['community']) #send id of community, not name
    db_session.add(sub)
    db_session.commit()
    return jsonify({'SUCCESS':'you JUST SUBSCRIBED TO SOMETHING'})

@app.route('/api/location/add', methods=['POST'])
def add_location():
    if not request.json:
        print 'no json'
        return jsonify({'error' : "yo where's the json man"})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:
        return jsonify({'error' : "wrong username and/or password"})
    lat = float(request.json['lat'])
    long = float(request.json['long'])
    community = str(request.json['community'])
    if Community.query.filter(Community.name==community).count()==0:
        return jsonify({'error':'community does not exist'})
    name = str(request.json['name'])
    description = str(request.json['description'])
    location = Location(lat=lat, long=long, community=community, name=name, description=description)
    db_session.add(location)
    db_session.commit()
    print "added %s to the database" % (name)    
    return jsonify({'response':'thank you come again'})

@app.route('/api/location/remove', methods=['POST'])
def remove_location():
    pass

@app.route('/api/location/find', methods=['POST'])
def find_locations():
    if not request.json:
        return jsonify({'error' : "yo where's the json man"})
    
    locations = query_locations(lat_user=request.json['lat'], long_user=request.json['long'], communities=[community for community in request.json['communities']], radius=request.json['radius'])
    return jsonify(locations)

@app.route('/api/location/upvote', methods=['POST'])
def upvote():
    if not request.json:
        return jsonify({'error' : 'no json data received'})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:
        return jsonify({'error' : "wrong username and/or password"})
    location_id = request.json['id']
    location = Location.query.filter(Location.id==location_id).first()
    vote = Vote.query.filter(Vote.location == location_id).filter(Vote.user == user.id).first()
    print vote
    if vote == None:
        location.ep +=1
	vote = Vote(user = user.id, location = location_id, type = 1)
	db_session.add(vote)
        db_session.commit()
    elif vote.type == 0:
	location.ep-=2
	vote.type = 1
	db_session.commit()
    return "no"

@app.route('/api/location/downvote', methods=['POST'])
def downvote():
    if not request.json:
        return jsonify({'error' : 'no json data received'})
    user = check_login(request.json['user_name'], request.json['password'])
    if user == None:
        return jsonify({'error' : "wrong username and/or password"})
    location_id = request.json['id']
    location = Location.query.filter(Location.id==location_id).all()
    vote = Vote.query.filter(Vote.location == location_id).filter(Vote.user == user.id).first()
    if vote == None:
        location.ep -=1
	vote = Vote(user = user.id, location = location_id, type = 1)
	db_session.add(vote)
        db_session.commit()
    elif vote.type == 1:
	location.ep+=2
	vote.type = 0
	db_session.commit()
    return "no"

@app.route('/api/community/add', methods = ['POST'])
def add_community():
    print request.json
    if not request.json:
        return jsonify({'error' : "yo where's the json man"})
    print "i have recieived json"
    if Community.query.filter(Community.name==request.json['name']).count() >0:
        return jsonify({'error' : "cant make the same community twice man"})
    print "it has been added"
    community = Community(name=request.json['name'])
    db_session.add(community)
    db_session.commit()
    return jsonify({'community' : 'submitted'})

@app.route('/api/community/list', methods = ['POST','GET'])
def find_community():
    community_dict= ({})
    for community in list(Community.query.all()):
        community = row2dict(community)
        community_dict[community['name']]=community
    return jsonify(community_dict)

def query_locations(lat_user, long_user, communities, radius):
    goodlocations = []
    for community in communities:
        sql_query="SELECT * FROM locations HAVING locations.community='%s' AND (SQRT(POWER(%f-locations.lat,2)+POWER(%f-locations.long,2)))<='%f'" % (community, lat_user, long_user, radius) 
        locations = db_session.execute(sql_query)
        num_locations_found = 0;
        for location in locations:
            location = dict(zip(location.keys(), location))
            goodlocations.append(location)
            num_locations_found+=1
            if num_locations_found == 1000:
                break
    goodlocations_dict = ({})
    for location in goodlocations:
        goodlocations_dict[location['id']]=location
    return goodlocations_dict

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

def check_login(user_name, password):
    print user_name + " : " + password
    user = User.query.filter(User.user_name == user_name).first()
    if not user:
	return None
    print check_password_hash(user.password, password)
    if check_password_hash(user.password, password):
        print "logged"
        return user
        
    return None

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
