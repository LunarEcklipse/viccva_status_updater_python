import os, requests, logging, json
from datetime import datetime, timedelta
from time import sleep

absPath = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname = os.path.dirname(absPath)
os.chdir(dname)
logging.basicConfig(filename=os.path.join(dname, 'logs', 'twitch_update.txt'), filemode='a', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

class Twitch_Auth:
    def __init__(self, client_id: str, client_secret: str):
        self.ClientID = client_id
        self.ClientSecret = client_secret
        self.Authorization = None
        self.AuthExpiration = datetime.now()

    def GetAuthorization(self):
        url = "https://id.twitch.tv/oauth2/token"
        p = {"client_id": self.ClientID, "client_secret": self.ClientSecret, "grant_type": "client_credentials"}
        r = requests.post(url, params=p)
        if r.status_code != 200:
            logging.error(f"Request returned bad response. Response expected: 200. Response received: {str(r.status_code)}")
            return
        logging.info("Twitch response successful.")
        js = None
        try:
            js = r.json()
        except requests.exceptions.JSONDecodeError:
            logging.error(f"Could not decode JSON response. Response reads: \"{r.text}\"")
            return
        
        self.Authorization = js["access_token"]
        self.AuthExpiration = datetime.now() + timedelta(seconds=js["expires_in"])
        logging.info(f"Authorization key ready.")
        return
    
    def Validate(self) -> bool: # Returns whether or not the authorization is valid based on if it's expired or not.
        exp = self.AuthExpiration.timestamp()
        now = datetime.now().timestamp()
        if (exp - now) < 0:
            return False
        return True

    def GetSecondsRemaining(self) -> int: # Returns the approximate number of seconds left before the authorization key expires.
        exp = self.AuthExpiration.timestamp()
        now = datetime.now().timestamp()
        if (exp - now) < 0:
            return 0
        return (exp - now)

    def PreparedAuth(self) -> str:
        return f"Bearer {self.Authorization}"

def GetStreamData(User_ID: int, Client_ID: str, Auth: str):
    url = "https://api.twitch.tv/helix/streams"
    h = {'Authorization': Auth, "Client-Id": Client_ID}
    p = {'user_id': str(User_ID)}
    r = requests.get(url, headers=h, params=p)
    if r.status_code != 200:
        logging.error(f"Twitch returned non-standard response code: {str(r.status_code)} when acquiring stream data.")
        return
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dat', 'twitch_live_data.json'), 'w') as f:
        f.write(r.text)
    return

def GetUserData(User_ID: int, Client_ID: str, Auth: str):
    url = "https://api.twitch.tv/helix/users"
    h = {'Authorization': Auth, "Client-Id": Client_ID}
    p = {'id': str(User_ID)}
    r = requests.get(url, headers=h, params=p)
    if r.status_code != 200:
        logging.error(f"Twitch returned non-standard response code: {str(r.status_code)} when acquiring user data.")
        return
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dat', 'twitch_user_data.json'), 'w') as f:
        f.write(r.text)
    return

def GetChannelData(User_ID: int, Client_ID: str, Auth: str):
    url = "https://api.twitch.tv/helix/channels"
    h = {'Authorization': Auth, "Client-Id": Client_ID}
    p = {'broadcaster_id': str(User_ID)}
    r = requests.get(url, headers=h, params=p)
    if r.status_code != 200:
        logging.error(f"Twitch returned non-standard response code: {str(r.status_code)} when acquiring channel data.")
        return
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dat', 'twitch_channel_data.json'), 'w') as f:
        f.write(r.text)
    return

def main():
    ViccUserId = 518336885
    raw = None
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dat', 'twitch.json'), 'r') as f:
        raw = f.read()
    j = json.loads(raw)
    ClientID = j["client_id"]
    logging.info(f"Twitch Update Client starting with client ID: {ClientID}")
    auth = Twitch_Auth(ClientID, j["client_secret"])
    auth.GetAuthorization()
    ClientID = j["client_id"]
    del j, f, raw
    while True:
        if auth.GetSecondsRemaining() < 3600:
            logging.info("Refreshing Authorization token...")
            auth.GetAuthorization()
        GetStreamData(ViccUserId, ClientID, auth.PreparedAuth())
        GetUserData(ViccUserId, ClientID, auth.PreparedAuth())
        GetChannelData(ViccUserId, ClientID, auth.PreparedAuth())
        sleep(60)

# PREVENTS ERRORS FROM UNINTENTIONAL EXECUTION

if __name__ == "__main__":
    main()
