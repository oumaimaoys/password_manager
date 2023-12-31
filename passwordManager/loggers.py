import gitlab
import requests
from bmc import *
import json

class Logger():
    """
    Abstract logger class for platform-specific actions.
    """
    def __init__(self, token, url, id, password):
        self.platform_api_token = token # API token for authentication.
        self.platform_api_url = url #APi base URL
        self.login_id = id # Login ID for platforms that authenticate with admin credentials instead of token
        self.password = password # password for platforms that authenticate with admin credentials instead of token
        
    def make_request(self, method, endpoint, data, params):
        headers = {
            "Content-Type": "application/json"
        }
        if self.platform_api_token != "":
            headers["Authorization"] =  "Bearer " + self.platform_api_token
            auth= None
        else :
            auth= (self.login_id, self.password)
        
        url = self.platform_api_url + endpoint
        
        try:
            if method == 'get':
                response = requests.get(url, headers=headers, json=data, auth=auth, params=params)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=data, auth=auth)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=data, auth=auth)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, json=data, auth=auth)
            else:
                raise ValueError("Invalid HTTP method")

            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error: request to api failed {e}")
            return None


class GitlabLogger(Logger):
    def __init__(self, token, url, id , password):
        super().__init__(token, url, id , password)
        self.gl = gitlab.Gitlab(url=self.platform_api_url, private_token=self.platform_api_token)

    def create_user(self, email, user_name, name, password):
        user_data = {'email': email, 'username': user_name, 'name': name,'password':password, 'skip_confirmation': True}
        try:
            user = self.gl.users.create(user_data) 
            return user
        except Exception as e:
            print(f"user failed to be created: {e}")
        
    def block_user(self, id, user_name): # blocking them
        if id:
            user = self.gl.users.get(id) # by id       
        else:
            raise ValueError
        user.block()

    def unblock_user(self, id, user_name): # unblocking them
        if id:
            user = self.gl.users.get(id) # by id       
        else:
            raise ValueError
        return (user.unblock())
        

    def get_user_id(self,user_name):
        user = self.gl.users.list(username=user_name)[0]
        return user.id

    def get_users(self):
        users = self.gl.users.list(get_all=True)
        users_data = []
        for user in users:
            if user.state == "active":
                state = True
            else:
                state = False

            name = (user.name).split(' ', 1)
            if len(name) == 2:
                first_name = name[0]
                last_name = name[1]
            else :
                first_name = name[0]
                last_name = ""
            
            user_data = {"id":user.id, "username":user.username, "first name": first_name, "last name":last_name, "email":user.email, "status":state}
            users_data.append(user_data)
        return users_data


class MatterMostLogger(Logger):
    def __init__(self,token, url, id, password):
        super().__init__(token, url, id, password)

    def create_user(self, email, user_name, password,name):
        data = {
            "username": user_name,
            "password": password,
            "email": email
        }
        try: 
            return self.make_request(method="post",endpoint="", data=data, params={} )
        except Exception as e:
            print(f"user failed to be created: {e}")
    
    def block_user(self,id,user_name): #status = boolean
        endpoint = '/' + str(id) +"/active"
        data = { "active":  False}
        return self.make_request(method="put", endpoint=endpoint, data= data, params={} )  

    def unblock_user(self, id, user_name):
        endpoint = '/' + str(id) +"/active"
        data = { "active":  True}
        return self.make_request(method="put", endpoint=endpoint, data= data, params={} )  

    
    def delete_user(self,id,user_name): #permanent delete
        endpoint = '/' + str(id) 
        data = { "active":  False, "permanent":True}
        return self.make_request(method="delete", endpoint=endpoint, data= data, params={} )
    
    def get_user_id(self, user_name):
        endpoint = "/usernames"
        data = [user_name]
        user_data = self.make_request(method="post", endpoint=endpoint, data= data, params={} )
        user_decoded = json.loads(user_data.decode())
        return user_decoded[0]["id"]

    def get_users(self):
        users = self.make_request(method="get", endpoint="", data= {}, params={} )
        users_decoded = json.loads(users.decode())
        users_data = []
        for user in users_decoded:
            if user["delete_at"]==0:
                state = True
            else :
                state = False
            user = {"id":user["id"], "username":user["username"],"first name":user["first_name"],"last name":user["last_name"], "email":user["email"], "status":state}
            users_data.append(user)

        return users_data
    
class MinioLogger(Logger):
    def __init__(self,token, url, id, password) -> None:
        super().__init__(token, url, id, password)
        self.r = config_host_add(
                alias='infodat',
                url=self.platform_api_url,
                username=self.login_id,
                password= self.password,
                )


    def create_user(self, email, user_name, password, name):
        user = admin_user_add(target='infodat', username=user_name, password=password)
        try:
            return user.content
        except Exception as e:
            print(f"user failed to be created: {e}")

        
    def block_user(self,id, user_name): # disable user
        user = admin_user_disable(target='infodat', username=user_name)
        return user.content
    
    def unblock_user(self, id, user_name):
        user = admin_user_enable(target='infodat', username=user_name)
        return user.content
        
    def remove_user(self, user_name): #permanently  
        user = admin_user_remove(target="infodat",username=user_name)
        return user.content
    
    def get_user_id(self, user_name):
        return "000"
    
    def get_users(self):
        users = admin_user_list(target='infodat').content
        users_data = []
        for user in users:
            if user["userStatus"] == 'enabled':
                state = True
            else:
                state = False
            user_data  = {"id":000, "username":user["accessKey"], "first name":"", "last name":"", "email":"", "status":state}
            users_data.append(user_data)
        return users_data


class HarborLogger(Logger):
    def __init__(self,token, url, id, password) -> None:
        super().__init__(token, url, id, password)
   

    def create_user(self,email, user_name, name, password):
        data ={
            "username": user_name,
            "email": email, 
            "password": password, 
            "realname": name, 
        }
        try:
            return self.make_request(method="post",endpoint="", data=data , params={} )
        except Exception as e:
            print(f"user failed to be created: {e}")

    def block_user(self, id, user_name): #removes it but not permanently
        endpoint = "/"+ str(id)
        return self.make_request(method="delete",endpoint=endpoint, data={}, params={} )
    
    def unblock_user(self, id, user_name): # action not possible in harbor api
        return False
    
    def get_user_id(self, user_name):
        endpoint= "/search"
        params =  {"username": user_name}
        user_data = self.make_request(method="get", endpoint=endpoint, data={}, params=params )
        user_decoded = json.loads(user_data.decode())
        return user_decoded[0]["user_id"]


    def get_users(self): 
        """
            return a list of users
            each user : {"id", "username","first name","last name", "email", "status"}
        """
        users = self.make_request(method="get", endpoint="", data={}, params={} )
        users_decoded = json.loads(users.decode())
        users_data = []
        for user in users_decoded:
            name = (user["realname"]).split(' ', 1)
            if len(name) == 2:
                first_name = name[0]
                last_name = name[1]
            else :
                first_name = name[0]
                last_name = ""
            user = {"id":user["user_id"], "username":user["username"],"first name":first_name,"last name":last_name, "email":user["email"], "status":True}
            users_data.append(user)
        return users_data

