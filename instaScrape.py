#!python3
# Scrape your instagram followers

import time, json, os, sys, getpass
from InstagramAPI import InstagramAPI


class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    YELLOW = '\033[93m'
    
def getFollowers(userID):
    followers = []
    next_max_id = True
    while next_max_id:
        print(bcolors.YELLOW + 'Fetching Followers...' + bcolors.ENDC)
        #first iteration hack
        if next_max_id == True:
            next_max_id = ''
        _ = InstagramAPI.getUserFollowers(userID, maxid = next_max_id)
        followers.extend(InstagramAPI.LastJson.get('users', []))
        next_max_id = InstagramAPI.LastJson.get('next_max_id', '')
    time.sleep(1)

    followerList = followers
    return followerList

def getFollowing(userID):
    following = []
    next_max_id = True
    while next_max_id:
        print(bcolors.YELLOW + 'Fetching Following...' + bcolors.ENDC)
        #first iteration hack
        if next_max_id == True:
            next_max_id = ''
        _ = InstagramAPI.getUserFollowings(userID, maxid = next_max_id)
        following.extend(InstagramAPI.LastJson.get('users', []))
        next_max_id = InstagramAPI.LastJson.get('next_max_id', '')
    time.sleep(1)

    followingList = following
    return followingList

def getLog(username):
    rootDir = os.path.dirname(os.path.realpath(__file__)) + '/' + username + '_IGlogs'
    dataFile = username + '_IGlog.json'
    if not os.path.exists(rootDir + '/' + dataFile):
        return None
    with open(rootDir + '/' + dataFile, 'r') as f:
        userData = json.load(f)
        return userData

def getLost(oldFollowers, currentFollowers, oldLost, gained):
    totalLost = []
    
    #Get current Lost
    currentFollowerIDs = []
    for follower in currentFollowers:
        currentFollowerIDs.append(follower['pk'])
    for follower in oldFollowers:
        if follower['pk'] not in currentFollowerIDs:
            totalLost.append(follower)

    #Get old Lost
    try:
        for follower in oldLost:
            totalLost.append(follower)
    except TypeError:
        pass

    #check to see if gained in list/ remove gianed follower
    gainedFollowerIDs = []
    try:
        for follower in gained:
            gainedFollowerIDs.append(follower['pk'])
    except TypeError:
        pass

    for follower in totalLost:
        if follower['pk'] in gainedFollowerIDs:
            totalLost.remove(follower)

    #return totalLost
    if len(totalLost) < 1:
        return None
    else:
        return totalLost

def getGained(oldFollowers, currentFollowers):
    gained = []
    oldFollowerIDs = []

    # Gained Followers
    for follower in oldFollowers:
        oldFollowerIDs.append(follower['pk'])
    for follower in currentFollowers:
        if follower['pk'] not in oldFollowerIDs:
            gained.append(follower)
    
    if len(gained) < 1:
        return None
    else:
        return gained

def writeLog(username, followerList, followingList, lost):
    rootDir = os.path.dirname(os.path.realpath(__file__)) + '/' + username + '_IGlogs'
    #Create Log directory in !exist
    if not os.path.isdir(rootDir):
        os.makedirs(rootDir)
        print('created: ' + bcolors.GREEN + rootDir + bcolors.ENDC)

    #create/ overwrite Log
    filename = username + '_IGlog.json'
    with open(rootDir + '/' + filename, 'w') as f:
        fileData = {'Followers': followerList, 'Following': followingList, 'Lost': lost}
        json.dump(fileData, f, indent=2)
        print(bcolors.GREEN + filename + bcolors.ENDC + ' written at: ' + bcolors.GREEN+ rootDir + bcolors.ENDC)

def output(lost, gained):
    #print lost:
    print(bcolors.BLUE + 'Lost:' + bcolors.ENDC)
    try:
        for follower in lost:
            print(follower['username'])
    except TypeError:
        print('No lost Followers.')
    
    #print gained:
    print(bcolors.BLUE + 'Gained:' + bcolors.ENDC)
    try:
        for follower in gained:
            print(follower['username'])
    except TypeError:
        print('No gained Followers.')

# login to instagram
username = input('Enter account username: ')
password = getpass.getpass('Enter account password: ')

InstagramAPI = InstagramAPI(username, password)
if not InstagramAPI.login():
    sys.exit(bcolors.FAIL + 'Incorrect Password/ Username' + bcolors.ENDC)


#Get user Data
user_data = InstagramAPI.getProfileData()
user_id = InstagramAPI.LastJson['user']['pk']

#Get followers/ following
currentFollowers, currentFollowing = getFollowers(user_id), getFollowing(user_id)
oldData = getLog(username)


#If no old data found: write log and exit
if oldData == None:
    writeLog(username, currentFollowers, currentFollowing, None)
    sys.exit(bcolors.FAIL + 'Done.' + bcolors.ENDC)

#Retrieve old Follower Data
oldFollowers = oldData['Followers']
oldLost = oldData['Lost']
gained = getGained(oldFollowers, currentFollowers)
lost = getLost(oldFollowers, currentFollowers, oldLost, gained)

#print output
output(lost, gained)
writeLog(username, currentFollowers, currentFollowing, lost)