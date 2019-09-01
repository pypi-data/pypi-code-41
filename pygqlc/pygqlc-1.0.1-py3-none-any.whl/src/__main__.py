from .GraphQLClient import GraphQLClient 
def main():
  import os
  gql = GraphQLClient()
  gql.addEnvironment(
      'dev',
      os.environ.get('API'),
      default=True)
  gql.addHeader(
      environment='dev',
      header={'Authorization': os.environ.get('TOKEN')})

if __name__ == "__main__":
  main()
