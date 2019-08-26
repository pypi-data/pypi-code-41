import requests

class gitlabapi:
    adr=''
    token_i=''
    peer_page=''
    def __init__(self,adr2,token,p):
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

class registry(gitlabapi):

    def get_registry_repositories(self):
        #GET /projects/:id/registry/repositories
        r=requests.get(self.adr + str(id) +'/registry/repositories', params=self.token_i)
        return r.json()
     
    # Delete repository tags in bulk
    # Delete repository tags in bulk based on given criteria.
    # DELETE /projects/:id/registry/repositories/:repository_id/tags
    #   id	integer/string	yes	The ID or URL-encoded path of the project owned by the authenticated user.
    #   repository_id	integer	yes	The ID of registry repository.
    #   name_regex	string	yes	The regex of the name to delete. To delete all tags specify .*.
    #   keep_n	    integer no	The amount of latest tags of given name to keep.
    #   older_than	string	no	Tags to delete that are older than the given time, written in human readable form 1h, 1d, 1month.
    #   https://docs.gitlab.com/ee/api/container_registry.html
    
    def delete_registry_repositories(self,r_id,**data):
        for v,k in data.items():
            self.token_i[v]=k
        r=requests.delete(self.adr + str(id) +'/registry/repositories/'+ str(r_id) + "/tags" , params=self.token_i)
        return r.json()
     




    # Within a group
    # Get a list of registry repositories in a group.
    # GET /groups/:id/registry/repositories

    # Delete registry repository
    # Delete a repository in registry.
    # This operation is executed asynchronously and might take some time to get executed.
    # DELETE /projects/:id/registry/repositories/:repository_id

    # Within a project
    # Get a list of tags for given registry repository.
    # GET /projects/:id/registry/repositories/:repository_id/tags
 
    # Get details of a repository tag
    # Get details of a registry repository tag.
    # GET /projects/:id/registry/repositories/:repository_id/tags/:tag_name

    # Delete a repository tag
    # Delete a registry repository tag.
    # DELETE /projects/:id/registry/repositories/:repository_id/tags/:tag_name