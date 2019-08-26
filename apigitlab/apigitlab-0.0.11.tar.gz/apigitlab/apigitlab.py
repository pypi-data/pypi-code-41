import requests
class apigitlab:
    adr=''
    token_i=''
    
    def __init__(self,adr2,token):
        self.adr=adr2
        self.token_i=token
        
    def get_projects(self):
        r = requests.get(self.adr, params=self.token_i)
        t=tuple(r.json())
        array={}
        for i in t:
          array[i['name']]={'id':i['id'],'merge_requests':i['_links']['merge_requests'],'repo_branches':i['_links']['repo_branches'],'labels':i['_links']['labels'],'issues':i['_links']['issues']}
        return array
    
    def get_project_id(self,project):
        r = requests.get(self.adr, params=self.token_i)
        t=tuple(r.json())
        array={}
        for i in t:
          array[i['name']]={'id':i['id'],'merge_requests':i['_links']['merge_requests'],'repo_branches':i['_links']['repo_branches'],'labels':i['_links']['labels'],'issues':i['_links']['issues']}
        array=array[project]
        return array.get('id')
    
    def merge_requests_project(self,id):  
        r = requests.get(self.adr + str(id) +'/merge_requests?state=opened', params=self.token_i)
        return r.json()
    
    def get_pipelines(self,id,iid):
        t={}
        self.token_i['per_page']=20
        r = requests.get(self.adr + str(id) +'/merge_requests/'+ str(iid) +'/pipelines', params=self.token_i)
        t=r.json()
        while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr + str(id) +'/merge_requests/'+ str(iid) +'/pipelines', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break
        return t
    
    def cancel_pipelines(self,id,pid):
        r = requests.post(self.adr + str(id) +'/pipelines/'+ str(pid) +'/cancel', params=self.token_i)
        print(r.url)
        return r.json()
    
    def get_pipelines_project(self,id):
        t={}
        self.token_i['per_page']=20
        r = requests.get(self.adr + str(id) +'/pipelines', params=self.token_i)
        t=r.json()
        while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr + str(id) +'/pipelines', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break
        return t
    
    def get_commit(self,id):
      r = requests.get(self.adr + str(id) +'/repository/commits', params=self.token_i)
      print(tuple(r.json()))
      print("_______")
    
    def get_branch(self,id,branch):
      r = requests.get(self.adr+ str(id) +'/repository/branches/'+ branch , params=self.token_i)
      ret=r.json()
      #print(ret)
      if ret.get('message'):
          return ret
      else:    
       return ret['commit']['id'] 
      
    def get_reg_con(self,id):
      self.token_i['per_page']=20
      r = requests.get(self.adr+ str(id) +'/registry/repositories', params=self.token_i)
      t=r.json()
      while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr+ str(id) +'/registry/repositories', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break

      return t

class agitlabapi:
   def __init__(self,adr2,token,api,per_page):
        self.adr=adr2
        self.token_i=token
        self.api=api
        self.per_page=per_page

   





    
