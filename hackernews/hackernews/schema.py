import graphene
import graphql_jwt


import links.schema
import users.schema
import links.schema_relay

class Query(
    users.schema.Query,
    links.schema.Query,
    links.schema_relay.RelayQuery,
    graphene.ObjectType,
):
    pass

class Mutation(users.schema.Mutation, links.schema.Mutation, graphene.ObjectType, links.schema_relay.RelayMutation):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field() # -> Mutation to authenticate users
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)